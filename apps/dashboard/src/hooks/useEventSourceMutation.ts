import { useCallback } from 'react';
import { api } from '@/api/client';
import type {
	EventSource,
	EventSourceCreate,
	EventSourceMetadataUpdate,
	IngestionCredentialCreate,
	IngestionCredential,
	IssuedIngestionCredential,
} from '@/api/contracts';
import { useMutation } from './useMutation';

type EventSourceUpdateInput = {
	id: string;
	body: EventSourceMetadataUpdate;
};

type EventSourceStatusInput = {
	id: string;
	active: boolean;
};

export function useEventSourceMutation(tenantId: string | undefined) {
	const create = useMutation<EventSourceCreate, EventSource>(
		useCallback(
			(body) =>
				tenantId
					? api.createEventSource(tenantId, body)
					: Promise.reject(new Error('No tenant selected')),
			[tenantId],
		),
	);
	const update = useMutation<EventSourceUpdateInput, EventSource>(
		useCallback(({ id, body }) => api.updateEventSource(id, body), []),
	);
	const setStatus = useMutation<EventSourceStatusInput, EventSource>(
		useCallback(
			({ id, active }) =>
				active ? api.activateEventSource(id) : api.disableEventSource(id),
			[],
		),
	);
	const issueCredential = useMutation<
		IngestionCredentialCreate,
		IssuedIngestionCredential
	>(
		useCallback(
			(body) =>
				tenantId
					? api.issueCredential(tenantId, body)
					: Promise.reject(new Error('No tenant selected')),
			[tenantId],
		),
	);
	const rotateCredential = useMutation<string, IssuedIngestionCredential>(
		useCallback((id) => api.rotateCredential(id), []),
	);
	const revokeCredential = useMutation<string, IngestionCredential>(
		useCallback((id) => api.revokeCredential(id), []),
	);

	return {
		create,
		update,
		setStatus,
		issueCredential,
		rotateCredential,
		revokeCredential,
	};
}
