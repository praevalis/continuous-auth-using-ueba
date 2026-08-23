import { useCallback } from 'react';
import { api } from '@/api/client';
import type { ProviderRegistry } from '@/api/contracts';
import type { ProviderConnectionView } from '@/features/settings/provider-connections/types';
import { useAsyncResource } from './useAsyncResource';

export function useProviderConnections(tenantId: string | undefined) {
	const load = useCallback(async (): Promise<{
		connections: ProviderConnectionView[];
		providers: ProviderRegistry[];
	} | null> => {
		if (!tenantId) return null;
		const [connections, providers] = await Promise.all([
			api.listConnections(tenantId),
			api.listProviders(),
		]);
		return {
			providers,
			connections: connections
				.map((connection) => ({
					...connection,
					provider: providers.find(
						(item) => item.id === connection.provider_registry_id,
					),
				}))
				.filter(
					(connection): connection is ProviderConnectionView =>
						!!connection.provider,
				),
		};
	}, [tenantId]);
	return useAsyncResource(load, !!tenantId);
}
