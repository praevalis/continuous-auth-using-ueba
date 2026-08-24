import { useCallback } from 'react';
import { api } from '@/api/client';
import { useAsyncResource } from './useAsyncResource';

export type OverviewData = {
	pipelineHealth: Awaited<ReturnType<typeof api.getPipelineHealth>>;
	activityTrend: Awaited<ReturnType<typeof api.getActivityTrends>>;
	riskSummary: Awaited<ReturnType<typeof api.getRiskSummary>>;
	events: Awaited<ReturnType<typeof api.listEvents>>;
	decisions: Awaited<ReturnType<typeof api.listDecisions>>;
	cautionDecisions: Awaited<ReturnType<typeof api.listDecisions>>;
	lockoutDecisions: Awaited<ReturnType<typeof api.listDecisions>>;
	alerts: Awaited<ReturnType<typeof api.listAlerts>>;
	actions: Awaited<ReturnType<typeof api.listActions>>;
	skippedActions: Awaited<ReturnType<typeof api.listActions>>;
};

export function useOverview(tenantId: string | undefined) {
	const load = useCallback(async (): Promise<OverviewData | null> => {
		if (!tenantId) return null;

		const [events, earliestEvent] = await Promise.all([
			api.listEvents(tenantId, {
				sort: '-occurred_at',
				limit: 4,
				offset: 0,
			}),
			api.listEvents(tenantId, {
				sort: 'occurred_at',
				limit: 1,
				offset: 0,
			}),
		]);
		const occurredBefore = new Date().toISOString();
		const occurredAfter =
			earliestEvent.items[0]?.occurred_at ??
			new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

		const [
			pipelineHealth,
			activityTrend,
			riskSummary,
			decisions,
			cautionDecisions,
			lockoutDecisions,
			alerts,
			actions,
			skippedActions,
		] = await Promise.all([
			api.getPipelineHealth(tenantId),
			api.getActivityTrends(tenantId, {
				occurred_after: occurredAfter,
				occurred_before: occurredBefore,
				interval: 'day',
			}),
			api.getRiskSummary(tenantId),
			api.listDecisions(tenantId, {
				sort: '-decided_at',
				limit: 100,
				offset: 0,
			}),
			api.listDecisions(tenantId, {
				decision_band: 'caution',
				limit: 1,
				offset: 0,
			}),
			api.listDecisions(tenantId, {
				decision_band: 'lockout',
				limit: 1,
				offset: 0,
			}),
			api.listAlerts(tenantId, {
				sort: '-created_at',
				limit: 4,
				offset: 0,
			}),
			api.listActions(tenantId, {
				sort: '-requested_at',
				limit: 100,
				offset: 0,
			}),
			api.listActions(tenantId, {
				status: 'skipped',
				limit: 1,
				offset: 0,
			}),
		]);

		return {
			pipelineHealth,
			activityTrend,
			riskSummary,
			events,
			decisions,
			cautionDecisions,
			lockoutDecisions,
			alerts,
			actions,
			skippedActions,
		};
	}, [tenantId]);

	return useAsyncResource(load, !!tenantId);
}
