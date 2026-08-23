import { useCallback } from 'react';
import { api } from '@/api/client';
import { useAsyncResource } from './useAsyncResource';

export function usePolicies(tenantId: string | undefined) {
	const load = useCallback(async () => {
		if (!tenantId) return null;
		const [profiles, modes] = await Promise.all([
			api.listProfiles(tenantId),
			api.listModes(tenantId),
		]);
		return {
			profiles,
			mode: modes.find((item) => item.is_active)?.mode ?? 'shadow',
		};
	}, [tenantId]);
	return useAsyncResource(load, !!tenantId);
}
