import { useCallback } from 'react';
import { api } from '@/api/client';
import type { ActivitySection } from '@/features/activity/types';
import {
	mapAlertToActivityEntry,
	mapEnforcementActionToActivityEntry,
	mapPolicyDecisionToActivityEntry,
} from '@/features/activity/adapters';
import { useAsyncResource } from './useAsyncResource';

export function useActivity(
	tenantId: string | undefined,
	range: { from: string; to: string },
) {
	const load = useCallback(async (): Promise<ActivitySection[] | null> => {
		if (!tenantId) return null;

		const createdAfter = new Date(range.from).toISOString();
		const createdBefore = new Date(range.to).toISOString();
		const [alerts, decisions, actions] = await Promise.all([
			api.listAlerts(tenantId, {
				created_after: createdAfter,
				created_before: createdBefore,
				limit: 100,
				sort: '-created_at',
			}),
			api.listDecisions(tenantId, {
				decided_after: createdAfter,
				decided_before: createdBefore,
				limit: 100,
				sort: '-decided_at',
			}),
			api.listActions(tenantId, {
				requested_after: createdAfter,
				requested_before: createdBefore,
				limit: 100,
				sort: '-requested_at',
			}),
		]);
		return [
			{
				id: 'analysis',
				title: 'Analysis',
				statItems: [
					{
						value: String(decisions.pagination.total_count),
						label: 'decisions analyzed',
						tone: 'safe',
					},
				],
				entries: decisions.items.map(mapPolicyDecisionToActivityEntry),
			},
			{
				id: 'decisions',
				title: 'Alerts',
				statItems: [
					{
						value: String(alerts.pagination.total_count),
						label: 'alerts generated',
						tone: 'caution',
					},
				],
				entries: alerts.items.map(mapAlertToActivityEntry),
			},
			{
				id: 'response',
				title: 'Response activity',
				statItems: [
					{
						value: String(actions.pagination.total_count),
						label: 'responses recorded',
						tone: 'safe',
					},
				],
				entries: actions.items.map(mapEnforcementActionToActivityEntry),
			},
		];
	}, [range.from, range.to, tenantId]);
	return useAsyncResource(load, !!tenantId);
}
