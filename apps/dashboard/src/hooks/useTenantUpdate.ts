import { useCallback } from 'react';
import { api } from '@/api/client';
import type { TenantUpdate } from '@/api/contracts';
import { useMutation } from './useMutation';

export function useTenantUpdate(tenantId: string | undefined) {
	const mutate = useCallback(
		(body: TenantUpdate) => {
			return tenantId
				? api.updateTenant(tenantId, body)
				: Promise.reject(new Error('No tenant selected'));
		},
		[tenantId],
	);
	return useMutation(mutate);
}
