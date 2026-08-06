from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

import httpx
from domain.exceptions import InvalidProviderConnectionConfigurationError
from domain.policy import PolicyAction

from integrations.models import (
	OutboundActionExecutionRequest,
	OutboundActionExecutionResult,
	ProviderConnectionContext,
	ProviderConnectionSecrets,
	ProviderConnectionTestResult,
)


class KeycloakOutboundAdapter:
	"""Execute outbound enforcement actions against Keycloak."""

	@property
	def provider_key(self) -> str:
		"""Return the stable provider key supported by this adapter.

		Returns:
			The stable Keycloak provider key.
		"""
		return 'keycloak'

	async def test_connection(
		self,
		context: ProviderConnectionContext,
		secrets: ProviderConnectionSecrets,
	) -> ProviderConnectionTestResult:
		"""Validate a Keycloak connection with the configured credentials.

		Args:
			context: The provider connection metadata.
			secrets: The resolved provider connection secrets.

		Returns:
			The provider connection test result.
		"""
		tested_at = datetime.now(UTC)

		try:
			async with httpx.AsyncClient(timeout=10.0) as client:
				access_token = await self._fetch_access_token(client, context, secrets)
				realm_name = (
					context.external_tenant_reference or context.auth_realm or 'master'
				)

				response = await client.get(
					self._admin_url(context, f'/admin/realms/{quote(realm_name)}'),
					headers=self._authorization_headers(access_token),
				)
				response.raise_for_status()

				payload = response.json()

		except httpx.HTTPStatusError as error:
			return ProviderConnectionTestResult(
				success=False,
				tested_at=tested_at,
				error_code=f'http_{error.response.status_code}',
				error_message='Keycloak rejected the connection test request.',
				response_metadata={
					'provider': self.provider_key,
					'status_code': error.response.status_code,
				},
			)

		except httpx.HTTPError as error:
			return ProviderConnectionTestResult(
				success=False,
				tested_at=tested_at,
				error_code='network_error',
				error_message='Keycloak connection test failed due to a network error.',
				response_metadata={
					'provider': self.provider_key,
					'error_type': type(error).__name__,
				},
			)

		return ProviderConnectionTestResult(
			success=True,
			tested_at=tested_at,
			response_metadata={
				'provider': self.provider_key,
				'realm': payload.get('realm', realm_name),
				'display_name': payload.get('displayName'),
			},
		)

	async def execute_action(
		self,
		context: ProviderConnectionContext,
		secrets: ProviderConnectionSecrets,
		request: OutboundActionExecutionRequest,
	) -> OutboundActionExecutionResult:
		"""Execute one Keycloak outbound enforcement action.

		Args:
			context: The provider connection metadata.
			secrets: The resolved provider connection secrets.
			request: The outbound enforcement request.

		Returns:
			The outbound execution result.
		"""
		completed_at = datetime.now(UTC)
		request_payload_redacted = {
			'action': request.action.value,
			'connection_name': context.connection_name,
			'provider_key': context.provider_key,
			'realm': context.external_tenant_reference
			or context.auth_realm
			or 'master',
			'target_user_identifier': '[redacted]',
		}

		try:
			async with httpx.AsyncClient(timeout=10.0) as client:
				access_token = await self._fetch_access_token(client, context, secrets)
				user = await self._find_user(
					client,
					context,
					request.target_user_identifier,
					access_token,
				)

				if request.action is PolicyAction.LOCK_ACCOUNT:
					await self._lock_account(client, context, user, access_token)

				elif request.action is PolicyAction.TERMINATE_SESSION:
					await self._terminate_session(client, context, user, access_token)

				elif request.action is PolicyAction.STEP_UP_MFA:
					await self._require_mfa(client, context, user, access_token)

				else:
					return OutboundActionExecutionResult(
						success=False,
						completed_at=completed_at,
						request_payload_redacted=request_payload_redacted,
						error_code='unsupported_action',
						error_message=(
							f'Keycloak adapter does not support action '
							f'"{request.action.value}".'
						),
					)

		except _KeycloakUserNotFoundError:
			return OutboundActionExecutionResult(
				success=False,
				completed_at=completed_at,
				request_payload_redacted=request_payload_redacted,
				error_code='user_not_found',
				error_message='Keycloak user could not be resolved for enforcement.',
			)

		except httpx.HTTPStatusError as error:
			return OutboundActionExecutionResult(
				success=False,
				completed_at=completed_at,
				request_payload_redacted=request_payload_redacted,
				error_code=f'http_{error.response.status_code}',
				error_message='Keycloak rejected the outbound enforcement request.',
				response_metadata={'status_code': error.response.status_code},
			)

		except httpx.HTTPError as error:
			return OutboundActionExecutionResult(
				success=False,
				completed_at=completed_at,
				request_payload_redacted=request_payload_redacted,
				error_code='network_error',
				error_message='Keycloak outbound enforcement failed due to a network error.',
				response_metadata={'error_type': type(error).__name__},
			)

		return OutboundActionExecutionResult(
			success=True,
			completed_at=completed_at,
			request_payload_redacted=request_payload_redacted,
			external_action_id=(
				f'{self.provider_key}:{request.action.value}:{request.policy_decision_id}'
			),
		)

	async def _fetch_access_token(
		self,
		client: httpx.AsyncClient,
		context: ProviderConnectionContext,
		secrets: ProviderConnectionSecrets,
	) -> str:
		"""Return an access token for Keycloak admin API calls.

		Args:
			client: The HTTP client used for the request.
			context: The provider connection metadata.
			secrets: The resolved provider connection secrets.

		Returns:
			The bearer access token.
		"""
		response = await client.post(
			self._token_url(context),
			data={
				'grant_type': 'client_credentials',
				'client_id': context.client_id or '',
				'client_secret': secrets.client_secret or '',
			},
			headers={'Content-Type': 'application/x-www-form-urlencoded'},
		)
		response.raise_for_status()
		payload = response.json()
		access_token = payload.get('access_token')

		if not isinstance(access_token, str) or not access_token:
			raise InvalidProviderConnectionConfigurationError(
				'Keycloak token response did not include a valid access_token.'
			)

		return access_token

	async def _find_user(
		self,
		client: httpx.AsyncClient,
		context: ProviderConnectionContext,
		target_user_identifier: str,
		access_token: str,
	) -> dict[str, Any]:
		"""Resolve a Keycloak user representation by username.

		Args:
			client: The HTTP client used for the request.
			context: The provider connection metadata.
			target_user_identifier: The provider-side user identifier.
			access_token: The bearer access token.

		Returns:
			The resolved Keycloak user representation.

		Raises:
			_KeycloakUserNotFoundError: If no matching user exists.
		"""
		realm_name = context.external_tenant_reference or context.auth_realm or 'master'
		response = await client.get(
			self._admin_url(context, f'/admin/realms/{quote(realm_name)}/users'),
			params={'username': target_user_identifier, 'exact': 'true'},
			headers=self._authorization_headers(access_token),
		)
		response.raise_for_status()

		users = response.json()
		if not isinstance(users, list):
			raise InvalidProviderConnectionConfigurationError(
				'Keycloak user search response did not return a list.'
			)

		if not users:
			raise _KeycloakUserNotFoundError

		user = users[0]
		if not isinstance(user, dict):
			raise InvalidProviderConnectionConfigurationError(
				'Keycloak user search response did not return a valid user object.'
			)

		return user

	async def _lock_account(
		self,
		client: httpx.AsyncClient,
		context: ProviderConnectionContext,
		user: dict[str, Any],
		access_token: str,
	) -> None:
		"""Disable a Keycloak user account.

		Args:
			client: The HTTP client used for the request.
			context: The provider connection metadata.
			user: The resolved Keycloak user representation.
			access_token: The bearer access token.
		"""
		realm_name = context.external_tenant_reference or context.auth_realm or 'master'
		user_id = self._user_id(user)
		updated_user = dict(user)
		updated_user['enabled'] = False

		response = await client.put(
			self._admin_url(
				context,
				f'/admin/realms/{quote(realm_name)}/users/{quote(user_id)}',
			),
			json=updated_user,
			headers=self._authorization_headers(access_token),
		)
		response.raise_for_status()

	async def _terminate_session(
		self,
		client: httpx.AsyncClient,
		context: ProviderConnectionContext,
		user: dict[str, Any],
		access_token: str,
	) -> None:
		"""Terminate all active sessions for a Keycloak user.

		Args:
			client: The HTTP client used for the request.
			context: The provider connection metadata.
			user: The resolved Keycloak user representation.
			access_token: The bearer access token.
		"""
		realm_name = context.external_tenant_reference or context.auth_realm or 'master'
		user_id = self._user_id(user)
		response = await client.post(
			self._admin_url(
				context,
				f'/admin/realms/{quote(realm_name)}/users/{quote(user_id)}/logout',
			),
			headers=self._authorization_headers(access_token),
		)
		response.raise_for_status()

	async def _require_mfa(
		self,
		client: httpx.AsyncClient,
		context: ProviderConnectionContext,
		user: dict[str, Any],
		access_token: str,
	) -> None:
		"""Require MFA configuration for a Keycloak user on the next login.

		Args:
			client: The HTTP client used for the request.
			context: The provider connection metadata.
			user: The resolved Keycloak user representation.
			access_token: The bearer access token.
		"""
		realm_name = context.external_tenant_reference or context.auth_realm or 'master'
		user_id = self._user_id(user)
		required_actions = list(user.get('requiredActions') or [])

		if 'CONFIGURE_TOTP' not in required_actions:
			required_actions.append('CONFIGURE_TOTP')

		updated_user = dict(user)
		updated_user['requiredActions'] = required_actions

		response = await client.put(
			self._admin_url(
				context,
				f'/admin/realms/{quote(realm_name)}/users/{quote(user_id)}',
			),
			json=updated_user,
			headers=self._authorization_headers(access_token),
		)
		response.raise_for_status()

	@staticmethod
	def _user_id(user: dict[str, Any]) -> str:
		"""Return the Keycloak user identifier from a user representation.

		Args:
			user: The resolved Keycloak user representation.

		Returns:
			The Keycloak user identifier.

		Raises:
			InvalidProviderConnectionConfigurationError: If the user representation
				does not include a valid identifier.
		"""
		user_id = user.get('id')
		if not isinstance(user_id, str) or not user_id:
			raise InvalidProviderConnectionConfigurationError(
				'Keycloak user response did not include a valid id.'
			)

		return user_id

	@staticmethod
	def _authorization_headers(access_token: str) -> dict[str, str]:
		"""Return the authorization headers for one Keycloak admin request.

		Args:
			access_token: The bearer access token.

		Returns:
			The authorization headers mapping.
		"""
		return {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json',
		}

	@staticmethod
	def _admin_url(context: ProviderConnectionContext, path: str) -> str:
		"""Return an absolute Keycloak admin API URL.

		Args:
			context: The provider connection metadata.
			path: The URL path to append.

		Returns:
			The absolute admin API URL.
		"""
		return f'{context.base_url.rstrip("/")}{path}'

	@staticmethod
	def _token_url(context: ProviderConnectionContext) -> str:
		"""Return the Keycloak token endpoint URL.

		Args:
			context: The provider connection metadata.

		Returns:
			The token endpoint URL.
		"""
		realm_name = quote(context.auth_realm or 'master')
		return (
			f'{context.base_url.rstrip("/")}/realms/{realm_name}'
			'/protocol/openid-connect/token'
		)


class _KeycloakUserNotFoundError(Exception):
	"""Internal marker raised when a Keycloak user cannot be resolved."""
