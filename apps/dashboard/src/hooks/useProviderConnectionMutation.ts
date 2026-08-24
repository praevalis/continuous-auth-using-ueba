import { useCallback } from 'react';
import { api } from '@/api/client';
import type {
	ProviderConnectionTestResult,
	TenantProviderConnection,
	TenantProviderConnectionCreate,
	TenantProviderConnectionUpdate,
} from '@/api/contracts';
import { useMutation } from './useMutation';

type UpdateInput = {
	id: string;
	body: TenantProviderConnectionUpdate;
};

type StatusInput = {
	id: string;
	active: boolean;
};

type TestResult = ProviderConnectionTestResult;

export function useProviderConnectionMutation(tenantId: string | undefined) {
	const create = useMutation<
		TenantProviderConnectionCreate,
		TenantProviderConnection
	>(
		useCallback(
			(body) =>
				tenantId
					? api.createConnection(tenantId, body)
					: Promise.reject(new Error('No tenant selected')),
			[tenantId],
		),
	);
	const update = useMutation<UpdateInput, TenantProviderConnection>(
		useCallback(
			({ id, body }) =>
				tenantId
					? api.updateConnection(tenantId, id, body)
					: Promise.reject(new Error('No tenant selected')),
			[tenantId],
		),
	);
	const setStatus = useMutation<StatusInput, TenantProviderConnection>(
		useCallback(
			({ id, active }) =>
				tenantId
					? active
						? api.activateConnection(tenantId, id)
						: api.disableConnection(tenantId, id)
					: Promise.reject(new Error('No tenant selected')),
			[tenantId],
		),
	);
	const test = useMutation<string, TestResult>(
		useCallback(
			(id) =>
				tenantId
					? api.testConnection(tenantId, id)
					: Promise.reject(new Error('No tenant selected')),
			[tenantId],
		),
	);

	return { create, update, setStatus, test };
}
