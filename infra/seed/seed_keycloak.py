"""Bootstrap the local Keycloak demo and activate its platform connection."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

SEED_DIR = Path(__file__).resolve().parent


class _ApiError(RuntimeError):
	"""Represent an unsuccessful Keycloak or platform API operation."""

	def __init__(self, message: str, *, status_code: int | None = None) -> None:
		super().__init__(message)
		self.status_code = status_code


class _JsonApiClient:
	"""Issue small JSON and form-encoded HTTP requests."""

	def __init__(self, base_url: str) -> None:
		self.base_url = base_url.rstrip('/')

	def request(
		self,
		method: str,
		path: str,
		body: Any = None,
		*,
		query: dict[str, Any] | None = None,
		token: str | None = None,
		form: bool = False,
		timeout: float = 30,
	) -> Any:
		"""Send one request and decode its optional JSON response."""
		suffix = f'?{urlencode(query)}' if query else ''
		headers = {'Accept': 'application/json'}
		if token:
			headers['Authorization'] = f'Bearer {token}'

		payload = None
		if body is not None:
			if form:
				payload = urlencode(body).encode('utf-8')
				headers['Content-Type'] = 'application/x-www-form-urlencoded'
			else:
				payload = json.dumps(body).encode('utf-8')
				headers['Content-Type'] = 'application/json'

		request = Request(
			f'{self.base_url}{path}{suffix}',
			data=payload,
			headers=headers,
			method=method,
		)
		try:
			with urlopen(request, timeout=timeout) as response:
				raw = response.read()
		except HTTPError as error:
			detail = error.read().decode('utf-8', errors='replace')
			raise _ApiError(
				f'{method} {path} returned HTTP {error.code}: {detail}',
				status_code=error.code,
			) from error
		except URLError as error:
			raise _ApiError(f'{method} {path} failed: {error.reason}') from error

		return json.loads(raw) if raw else None


def _load_seed(path: Path) -> dict[str, Any]:
	return json.loads(path.read_text(encoding='utf-8'))


def _wait_for_keycloak(client: _JsonApiClient, timeout_seconds: int) -> None:
	deadline = time.monotonic() + timeout_seconds
	while time.monotonic() < deadline:
		try:
			client.request('GET', '/realms/master', timeout=5)
			return
		except _ApiError:
			time.sleep(2)
	raise TimeoutError(
		f'Keycloak did not become ready within {timeout_seconds} seconds.'
	)


def _admin_token(client: _JsonApiClient) -> str:
	response = client.request(
		'POST',
		'/realms/master/protocol/openid-connect/token',
		{
			'grant_type': 'password',
			'client_id': 'admin-cli',
			'username': os.environ.get('KEYCLOAK_ADMIN_USERNAME', 'admin'),
			'password': os.environ.get('KEYCLOAK_ADMIN_PASSWORD', 'admin'),
		},
		form=True,
	)
	if not isinstance(response, dict) or not isinstance(
		response.get('access_token'), str
	):
		raise _ApiError('Keycloak did not return an administrator access token.')
	return response['access_token']


def _ensure_realm(
	client: _JsonApiClient,
	token: str,
	realm_name: str,
	display_name: str,
) -> None:
	path = f'/admin/realms/{quote(realm_name, safe="")}'
	try:
		existing = client.request('GET', path, token=token)
	except _ApiError as error:
		if error.status_code != 404:
			raise
		client.request(
			'POST',
			'/admin/realms',
			{'realm': realm_name, 'displayName': display_name, 'enabled': True},
			token=token,
		)
		return

	if not isinstance(existing, dict):
		raise _ApiError('Keycloak returned an invalid realm representation.')
	client.request(
		'PUT',
		path,
		{**existing, 'displayName': display_name, 'enabled': True},
		token=token,
	)


def _single_item(items: Any, description: str) -> dict[str, Any] | None:
	if not isinstance(items, list):
		raise _ApiError(f'Keycloak returned an invalid {description} list.')
	if not items:
		return None
	item = items[0]
	if not isinstance(item, dict):
		raise _ApiError(f'Keycloak returned an invalid {description}.')
	return item


def _ensure_client(
	client: _JsonApiClient,
	token: str,
	realm_name: str,
	client_id: str,
	client_secret: str,
) -> dict[str, Any]:
	realm_path = quote(realm_name, safe='')
	clients_path = f'/admin/realms/{realm_path}/clients'
	existing = _single_item(
		client.request(
			'GET',
			clients_path,
			query={'clientId': client_id},
			token=token,
		),
		'client',
	)
	desired = {
		'clientId': client_id,
		'name': 'Continuous Auth outbound enforcement',
		'enabled': True,
		'protocol': 'openid-connect',
		'publicClient': False,
		'serviceAccountsEnabled': True,
		'standardFlowEnabled': False,
		'directAccessGrantsEnabled': False,
		'secret': client_secret,
	}
	if existing is None:
		client.request('POST', clients_path, desired, token=token)
		existing = _single_item(
			client.request(
				'GET',
				clients_path,
				query={'clientId': client_id},
				token=token,
			),
			'client',
		)
	else:
		client_uuid = str(existing.get('id', ''))
		if not client_uuid:
			raise _ApiError('Keycloak client did not include an identifier.')
		client.request(
			'PUT',
			f'{clients_path}/{quote(client_uuid, safe="")}',
			{**existing, **desired},
			token=token,
		)

	if existing is None or not existing.get('id'):
		raise _ApiError('Keycloak did not return the configured client.')
	return existing


def _ensure_service_account_roles(
	client: _JsonApiClient,
	token: str,
	realm_name: str,
	configured_client: dict[str, Any],
	role_names: list[str],
) -> None:
	realm_path = quote(realm_name, safe='')
	client_uuid = quote(str(configured_client['id']), safe='')
	service_account = client.request(
		'GET',
		f'/admin/realms/{realm_path}/clients/{client_uuid}/service-account-user',
		token=token,
	)
	if not isinstance(service_account, dict) or not service_account.get('id'):
		raise _ApiError('Keycloak did not return the client service-account user.')

	realm_management = _single_item(
		client.request(
			'GET',
			f'/admin/realms/{realm_path}/clients',
			query={'clientId': 'realm-management'},
			token=token,
		),
		'realm-management client',
	)
	if realm_management is None or not realm_management.get('id'):
		raise _ApiError('Keycloak realm-management client was not found.')

	management_uuid = quote(str(realm_management['id']), safe='')
	roles: list[dict[str, Any]] = []
	for role_name in role_names:
		role = client.request(
			'GET',
			f'/admin/realms/{realm_path}/clients/{management_uuid}/roles/'
			f'{quote(role_name, safe="")}',
			token=token,
		)
		if not isinstance(role, dict):
			raise _ApiError(f'Keycloak returned an invalid role for {role_name}.')
		roles.append(role)

	client.request(
		'POST',
		f'/admin/realms/{realm_path}/users/'
		f'{quote(str(service_account["id"]), safe="")}/role-mappings/clients/'
		f'{management_uuid}',
		roles,
		token=token,
	)


def _ensure_user(
	client: _JsonApiClient,
	token: str,
	realm_name: str,
	user_seed: dict[str, Any],
) -> None:
	realm_path = quote(realm_name, safe='')
	users_path = f'/admin/realms/{realm_path}/users'
	username = str(user_seed['username'])
	existing = _single_item(
		client.request(
			'GET',
			users_path,
			query={'username': username, 'exact': 'true'},
			token=token,
		),
		'user',
	)
	desired = {
		'username': username,
		'email': user_seed.get('email'),
		'firstName': user_seed.get('first_name'),
		'lastName': user_seed.get('last_name'),
		'enabled': True,
		'emailVerified': True,
	}
	if existing is None:
		client.request('POST', users_path, desired, token=token)
		existing = _single_item(
			client.request(
				'GET',
				users_path,
				query={'username': username, 'exact': 'true'},
				token=token,
			),
			'user',
		)
	else:
		client.request(
			'PUT',
			f'{users_path}/{quote(str(existing["id"]), safe="")}',
			{**existing, **desired},
			token=token,
		)

	if existing is None or not existing.get('id'):
		raise _ApiError(f'Keycloak did not return configured user {username}.')
	client.request(
		'PUT',
		f'{users_path}/{quote(str(existing["id"]), safe="")}/reset-password',
		{'type': 'password', 'value': str(user_seed['password']), 'temporary': False},
		token=token,
	)


def _items(response: Any) -> list[dict[str, Any]]:
	if isinstance(response, dict):
		response = response.get('items', [])
	return response if isinstance(response, list) else []


def _first_by(
	response: Any,
	property_name: str,
	expected: Any,
) -> dict[str, Any] | None:
	return next(
		(item for item in _items(response) if item.get(property_name) == expected),
		None,
	)


def _configure_platform(
	client: _JsonApiClient,
	seed: dict[str, Any],
	realm_name: str,
	client_id: str,
	secret_reference: str,
) -> None:
	tenants = client.request(
		'GET',
		'/tenants',
		query={'display_name': seed['tenant_display_name']},
	)
	tenant = _first_by(tenants, 'display_name', seed['tenant_display_name'])
	if tenant is None:
		raise _ApiError(
			f'Platform tenant {seed["tenant_display_name"]!r} was not found.'
		)
	tenant_id = str(tenant['id'])

	providers = client.request('GET', '/integrations/provider-registry')
	provider = _first_by(providers, 'provider_key', seed['provider_key'])
	if provider is None:
		raise _ApiError(f'Platform provider {seed["provider_key"]!r} was not found.')

	connections_path = '/integrations/tenant-provider-connections'
	connections = client.request(
		'GET', connections_path, query={'tenant_id': tenant_id}
	)
	connection = _first_by(
		connections,
		'connection_name',
		seed['connection_name'],
	)
	payload = {
		'connection_name': seed['connection_name'],
		'base_url': seed['base_url'],
		'auth_realm': realm_name,
		'client_id': client_id,
		'client_secret_ref': secret_reference,
		'external_tenant_reference': realm_name,
	}
	if connection is None:
		connection = client.request(
			'POST',
			connections_path,
			{'provider_registry_id': provider['id'], **payload},
			query={'tenant_id': tenant_id},
		)
	else:
		connection = client.request(
			'PATCH',
			f'{connections_path}/{connection["id"]}',
			payload,
			query={'tenant_id': tenant_id},
		)

	connection_id = str(connection['id'])
	test_result = client.request(
		'POST',
		f'{connections_path}/{connection_id}/test',
		query={'tenant_id': tenant_id},
	)
	if not isinstance(test_result, dict) or not test_result.get('success'):
		raise _ApiError(
			f'Platform rejected the Keycloak connection test: {test_result!r}'
		)
	client.request(
		'POST',
		f'{connections_path}/{connection_id}/activate',
		query={'tenant_id': tenant_id},
	)


def main() -> None:
	"""Configure the local Keycloak realm and connect the seeded tenant."""
	seed = _load_seed(SEED_DIR / 'keycloak-seed-data.json')
	keycloak = _JsonApiClient(
		os.environ.get('KEYCLOAK_BASE_URL', 'http://localhost:8081')
	)
	platform = _JsonApiClient(
		os.environ.get('CONTINUOUS_AUTH_API_URL', 'http://localhost:8000')
	)
	timeout_seconds = int(os.environ.get('KEYCLOAK_READY_TIMEOUT_SECONDS', '180'))

	print('Waiting for Keycloak...')
	_wait_for_keycloak(keycloak, timeout_seconds)
	token = _admin_token(keycloak)
	realm_seed = seed['realm']
	client_seed = seed['client']
	realm_name = str(realm_seed['name'])
	client_id = str(client_seed['client_id'])
	secret_reference = str(client_seed['secret_environment_variable'])
	client_secret = os.environ.get(secret_reference)
	if not client_secret:
		raise RuntimeError(
			f'Required demo client secret {secret_reference!r} is not configured.'
		)

	print(f'Configuring Keycloak realm {realm_name!r}...')
	_ensure_realm(keycloak, token, realm_name, str(realm_seed['display_name']))
	configured_client = _ensure_client(
		keycloak,
		token,
		realm_name,
		client_id,
		client_secret,
	)
	_ensure_service_account_roles(
		keycloak,
		token,
		realm_name,
		configured_client,
		[str(role) for role in client_seed['service_account_roles']],
	)
	for user_seed in seed['users']:
		_ensure_user(keycloak, token, realm_name, user_seed)

	print('Configuring the platform Keycloak connection...')
	_configure_platform(
		platform,
		seed['platform'],
		realm_name,
		client_id,
		secret_reference,
	)
	print('Keycloak demo seed complete; provider connection tested and activated.')


if __name__ == '__main__':
	main()
