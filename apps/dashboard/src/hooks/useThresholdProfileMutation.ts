import { useCallback } from 'react';
import { api } from '@/api/client';
import type { ThresholdProfileCreate } from '@/api/contracts';
import { useMutation } from './useMutation';

export function useThresholdProfileMutation(tenantId: string | undefined) {
	const mutate = useCallback(
		(body: ThresholdProfileCreate) =>
			tenantId
				? api.createProfile(tenantId, body)
				: Promise.reject(new Error('No tenant selected')),
		[tenantId],
	);

	return useMutation(mutate);
}
