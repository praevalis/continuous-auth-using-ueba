import { useCallback } from 'react';
import { api } from '@/api/client';
import type { OperatingModeCreate } from '@/api/contracts';
import { useMutation } from './useMutation';

export function usePolicyModeMutation(tenantId: string | undefined) {
	const mutate = useCallback(
		(body: OperatingModeCreate) => {
			return tenantId
				? api.createMode(tenantId, body)
				: Promise.reject(new Error('No tenant selected'));
		},
		[tenantId],
	);
	return useMutation(mutate);
}
