import type { EventSource, IngestionCredential } from '@/api/contracts';

export type EventSourceWithCredentials = EventSource & {
	credentials: IngestionCredential[];
};
