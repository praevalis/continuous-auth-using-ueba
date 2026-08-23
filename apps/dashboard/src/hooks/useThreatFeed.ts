import { useCallback } from 'react';
import { api } from '@/api/client';
import type { RiskSummary } from '@/api/contracts';
import { useAsyncResource } from './useAsyncResource';

export type ThreatFeedTimeRange = '24h' | '7d';

type ThreatFeedData = {
	events: Awaited<ReturnType<typeof api.listEvents>>;
	decisions: Awaited<ReturnType<typeof api.listDecisions>>;
	summary: RiskSummary;
};

function getOccurredAfter(timeRange: ThreatFeedTimeRange) {
	const duration = timeRange === '24h' ? 24 : 24 * 7;
	return new Date(Date.now() - duration * 60 * 60 * 1000).toISOString();
}

export function useThreatFeed(
	tenantId: string | undefined,
	timeRange: ThreatFeedTimeRange,
) {
	const load = useCallback(async (): Promise<ThreatFeedData | null> => {
		if (!tenantId) return null;
		const occurredAfter = getOccurredAfter(timeRange);
		const [events, decisions, summary] = await Promise.all([
			api.listEvents(tenantId, {
				limit: 100,
				offset: 0,
				sort: '-occurred_at',
				occurred_after: occurredAfter,
			}),
			api.listDecisions(tenantId, {
				limit: 100,
				offset: 0,
				sort: '-decided_at',
				decided_after: occurredAfter,
			}),
			api.getRiskSummary(tenantId, { occurred_after: occurredAfter }),
		]);
		return { events, decisions, summary };
	}, [tenantId, timeRange]);
	return useAsyncResource(load, !!tenantId);
}
