import type { components } from '@/api/generated/types';

export type ProviderRegistry = components['schemas']['ProviderRegistrySchema'];
export type TenantProviderConnection =
	components['schemas']['TenantProviderConnectionSchema'];
export type ProviderConnectionMethod =
	components['schemas']['ProviderConnectionMethod'];

export type ProviderConnectionView = TenantProviderConnection & {
	provider: ProviderRegistry;
};
