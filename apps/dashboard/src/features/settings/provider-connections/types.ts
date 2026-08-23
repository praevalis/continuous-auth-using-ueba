import type {
	ProviderRegistry,
	TenantProviderConnection,
} from '@/api/contracts';

export type { ProviderConnectionMethod } from '@/api/contracts';

export type ProviderConnectionView = TenantProviderConnection & {
	provider: ProviderRegistry;
};
