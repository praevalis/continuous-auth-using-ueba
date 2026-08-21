import type { components } from '@/api/generated/types';

export type EventSource = components['schemas']['EventSourceSchema'];
export type IngestionCredential =
	components['schemas']['IngestionCredentialSchema'];

export type EventSourceWithCredentials = EventSource & {
	credentials: IngestionCredential[];
};
