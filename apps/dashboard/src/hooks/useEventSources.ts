import { useCallback } from 'react';
import { api } from '@/api/client';
import type { EventSourceWithCredentials } from '@/features/settings/event-sources/types';
import { useAsyncResource } from './useAsyncResource';

export function useEventSources(tenantId: string | undefined) {
	const load = useCallback(async (): Promise<
		EventSourceWithCredentials[] | null
	> => {
		if (!tenantId) return null;
		const sources = await api.listEventSources(tenantId);
		return Promise.all(
			sources.map(async (source) => ({
				...source,
				credentials: await api.listCredentials(tenantId, source.id),
			})),
		);
	}, [tenantId]);
	return useAsyncResource(load, !!tenantId);
}
