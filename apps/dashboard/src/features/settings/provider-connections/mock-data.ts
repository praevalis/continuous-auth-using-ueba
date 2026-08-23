import type { components } from '@/api/generated/types';
import type { ProviderConnectionView } from './types';

const tenantId = 'tenant-demo';
const keycloakRegistryId = 'provider-registry-keycloak';

const keycloakProvider: components['schemas']['ProviderRegistrySchema'] = {
	id: keycloakRegistryId,
	provider_key: 'keycloak',
	display_name: 'Keycloak',
	provider_type: 'idp' as const,
	connection_method: 'oauth_client_credentials' as const,
	supported_policy_actions: ['step_up_mfa', 'terminate_session', 'alert_only'],
	is_active: true,
	deprecated_at: null,
	created_at: '2026-08-20T09:00:00Z',
	updated_at: '2026-08-20T09:00:00Z',
};

export const mockProviderConnections: ProviderConnectionView[] = [
	{
		id: 'provider-connection-primary',
		tenant_id: tenantId,
		provider_registry_id: keycloakRegistryId,
		connection_name: 'Keycloak response provider',
		base_url: 'https://keycloak.acme.example',
		auth_realm: 'continuous-auth',
		client_id: 'continuous-auth-response',
		client_secret_ref: 'secret-ref-primary',
		api_token_ref: null,
		external_tenant_reference: null,
		status: 'active',
		disabled_at: null,
		last_tested_at: '2026-08-22T09:24:00Z',
		last_test_error: null,
		created_at: '2026-08-20T09:24:00Z',
		updated_at: '2026-08-22T09:24:00Z',
		provider: keycloakProvider,
	},
	{
		id: 'provider-connection-backup',
		tenant_id: tenantId,
		provider_registry_id: keycloakRegistryId,
		connection_name: 'Keycloak backup connection',
		base_url: 'https://keycloak-backup.acme.example',
		auth_realm: 'continuous-auth-backup',
		client_id: 'continuous-auth-backup',
		client_secret_ref: 'secret-ref-backup',
		api_token_ref: null,
		external_tenant_reference: null,
		status: 'test_failed',
		disabled_at: null,
		last_tested_at: '2026-08-22T09:00:00Z',
		last_test_error: 'Connection test failed',
		created_at: '2026-08-20T09:24:00Z',
		updated_at: '2026-08-22T09:00:00Z',
		provider: keycloakProvider,
	},
];
