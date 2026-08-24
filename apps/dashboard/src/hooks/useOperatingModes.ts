import { useCallback } from 'react';
import { api } from '@/api/client';
import type { OperatingMode } from '@/api/contracts';
import { useAsyncResource } from './useAsyncResource';

export function useOperatingModes(tenantId: string | undefined) {
	const load = useCallback(async (): Promise<OperatingMode[] | null> => {
		if (!tenantId) return null;
		return api.listModes(tenantId);
	}, [tenantId]);

	return useAsyncResource(load, !!tenantId);
}
