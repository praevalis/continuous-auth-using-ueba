import argparse
import json
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SEED_DIR = Path(__file__).resolve().parent


def api_call(
	base_url: str,
	method: str,
	path: str,
	body: Any = None,
	headers: dict[str, str] | None = None,
) -> Any:
	payload = None if body is None else json.dumps(body).encode('utf-8')
	request_headers = {'Content-Type': 'application/json', **(headers or {})}
	request = Request(
		f'{base_url.rstrip("/")}{path}',
		data=payload,
		headers=request_headers,
		method=method,
	)

	try:
		with urlopen(request) as response:
			raw = response.read()
	except HTTPError as error:
		detail = error.read().decode('utf-8', errors='replace')
		raise RuntimeError(
			f'{method} {path} failed with HTTP {error.code}: {detail}'
		) from error

	return json.loads(raw) if raw else None


def first_by(items: Any, property_name: str, value: Any) -> dict[str, Any] | None:
	if isinstance(items, dict):
		items = items.get('items', [])
	return next(
		(item for item in items or [] if item.get(property_name) == value), None
	)


def load_json(path: Path) -> dict[str, Any]:
	return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:

	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('--base-url', default='http://localhost:8000')
	parser.add_argument('--seed-file', type=Path, default=SEED_DIR / 'seed-data.json')
	parser.add_argument('--state-file', type=Path, default=SEED_DIR / 'seed-state.json')
	parser.add_argument('--wait-for-worker', action='store_true')
	parser.add_argument('--worker-wait-seconds', type=int, default=20)
	args = parser.parse_args()

	seed = load_json(args.seed_file)
	state = load_json(args.state_file) if args.state_file.exists() else {}
	base_url = args.base_url.rstrip('/')

	api_seed = seed['api']
	providers = api_call(base_url, 'GET', '/integrations/provider-registry')
	provider = first_by(
		providers, 'provider_key', api_seed['provider_registry']['provider_key']
	)

	if provider is None:
		provider = api_call(
			base_url,
			'POST',
			'/integrations/provider-registry',
			api_seed['provider_registry'],
		)

	tenant = None
	if state.get('tenant_id'):
		try:
			tenant = api_call(base_url, 'GET', f'/tenants/{state["tenant_id"]}')
		except RuntimeError:
			tenant = None

	if tenant is None:
		onboarding = api_call(
			base_url, 'POST', '/tenants', api_seed['tenant_onboarding']
		)
		tenant = onboarding['tenant']

	tenant_id = tenant['id']
	sources = api_call(
		base_url, 'GET', f'/ingestion/event-sources?tenant_id={tenant_id}'
	)
	source = first_by(sources, 'source_name', api_seed['event_source']['source_name'])

	if source is None:
		source = api_call(
			base_url,
			'POST',
			f'/ingestion/event-sources?tenant_id={tenant_id}',
			api_seed['event_source'],
		)

	credentials = api_call(
		base_url, 'GET', f'/ingestion/ingestion-credentials?tenant_id={tenant_id}'
	)
	credential = first_by(
		credentials,
		'credential_name',
		api_seed['ingestion_credential']['credential_name'],
	)
	plaintext_secret = state.get('plaintext_secret')

	if credential is None:
		credential_request = {
			**api_seed['ingestion_credential'],
			'event_source_id': source['id'],
		}
		issued = api_call(
			base_url,
			'POST',
			f'/ingestion/ingestion-credentials?tenant_id={tenant_id}',
			credential_request,
		)
		credential, plaintext_secret = issued['credential'], issued['plaintext_secret']

	elif not plaintext_secret:
		issued = api_call(
			base_url,
			'POST',
			f'/ingestion/ingestion-credentials/{credential["id"]}/rotate',
		)
		credential, plaintext_secret = issued['credential'], issued['plaintext_secret']

	connections = api_call(
		base_url,
		'GET',
		f'/integrations/tenant-provider-connections?tenant_id={tenant_id}',
	)
	connection = first_by(
		connections,
		'connection_name',
		api_seed['provider_connection']['connection_name'],
	)
	if connection is None:
		connection_request = {
			**api_seed['provider_connection'],
			'provider_registry_id': provider['id'],
		}
		connection = api_call(
			base_url,
			'POST',
			f'/integrations/tenant-provider-connections?tenant_id={tenant_id}',
			connection_request,
		)

	accepted = api_call(
		base_url,
		'POST',
		'/ingestion/events',
		api_seed['event'],
		{
			'X-Ingestion-Key-Id': credential['key_id'],
			'X-Ingestion-Key-Secret': plaintext_secret,
		},
	)

	state = {
		'tenant_id': tenant_id,
		'provider_registry_id': provider['id'],
		'event_source_id': source['id'],
		'ingestion_credential_id': credential['id'],
		'tenant_provider_connection_id': connection['id'],
		'last_source_event_id': api_seed['event']['source_event_id'],
		'plaintext_secret': plaintext_secret,
		'last_accepted_at': accepted['accepted_at'],
	}
	args.state_file.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
	print(
		f'Seed accepted for tenant {tenant_id}; source event {api_seed["event"]["source_event_id"]}.'
	)
	print(f'Sensitive state written to {args.state_file}; do not commit it.')

	if args.wait_for_worker:
		deadline = time.monotonic() + args.worker_wait_seconds
		event = None

		while time.monotonic() < deadline and event is None:
			time.sleep(1)
			events = api_call(base_url, 'GET', f'/tenants/{tenant_id}/events?limit=50')
			event = first_by(
				events, 'source_event_id', api_seed['event']['source_event_id']
			)
		if event is None:
			print(
				'Warning: event accepted, but worker persistence was not visible before timeout.'
			)
		else:
			print(f'Worker persisted auth event {event["id"]}.')


if __name__ == '__main__':
	main()
