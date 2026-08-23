import { useCallback } from 'react';
import { api } from '@/api/client';
import { useAsyncResource } from './useAsyncResource';

export function useThreatFeedEvent(
	tenantId: string | undefined,
	eventId: string | undefined,
) {
	const load = useCallback(async () => {
		if (!tenantId || !eventId) return null;
		return api.getEvent(tenantId, eventId);
	}, [eventId, tenantId]);

	return useAsyncResource(load, !!tenantId && !!eventId);
}
