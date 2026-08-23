import { useCallback, useEffect, useState } from 'react';
import { api } from '@/api/client';
import { useTenant } from '@/api/tenant';
import PageLayout from '@/components/layout/PageLayout';
import ActivityIntro from './ActivityIntro';
import AuditControls from './AuditControls';
import ActivityLifecycle from './ActivityLifecycle';
import ActivityLifecycleTabs from './ActivityLifecycleTabs';
import {
	mapAlertToActivityEntry,
	mapEnforcementActionToActivityEntry,
	mapPolicyDecisionToActivityEntry,
} from './adapters';
import type { ActivitySection } from './types';
import type { ActivityKind } from './types';

const INITIAL_VISIBLE_COUNT = 6;

function toDateTimeValue(date: Date) {
	const pad = (value: number) => String(value).padStart(2, '0');
	return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function getInitialDateRange() {
	const to = new Date();
	const from = new Date(to);
	from.setHours(from.getHours() - 24);
	return { from: toDateTimeValue(from), to: toDateTimeValue(to) };
}

export default function Activity() {
	const [range, setRange] = useState(getInitialDateRange);
	const { tenant } = useTenant();
	const [sections, setSections] = useState<ActivitySection[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [selectedActivity, setSelectedActivity] =
		useState<ActivityKind>('analysis');
	const [visibleCounts, setVisibleCounts] = useState<
		Record<ActivityKind, number>
	>({
		analysis: INITIAL_VISIBLE_COUNT,
		decisions: INITIAL_VISIBLE_COUNT,
		response: INITIAL_VISIBLE_COUNT,
	});

	const load = useCallback(async () => {
		if (!tenant) return;
		setLoading(true);

		try {
			const params = {
				created_after: new Date(range.from).toISOString(),
				created_before: new Date(range.to).toISOString(),
				limit: 100,
				sort: '-created_at',
			};

			const [alerts, decisions, actions] = await Promise.all([
				api.listAlerts(tenant.id, params),
				api.listDecisions(tenant.id, {
					decided_after: params.created_after,
					decided_before: params.created_before,
					limit: 100,
					sort: '-decided_at',
				}),
				api.listActions(tenant.id, {
					requested_after: params.created_after,
					requested_before: params.created_before,
					limit: 100,
					sort: '-requested_at',
				}),
			]);

			setSections([
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
			]);
			setError(null);
		} catch (reason) {
			setError(
				reason instanceof Error ? reason.message : 'Unable to load activity',
			);
		} finally {
			setLoading(false);
		}
	}, [range.from, range.to, tenant]);

	useEffect(() => {
		queueMicrotask(() => void load());
	}, [load]);

	function resetActivity() {
		setVisibleCounts({
			analysis: INITIAL_VISIBLE_COUNT,
			decisions: INITIAL_VISIBLE_COUNT,
			response: INITIAL_VISIBLE_COUNT,
		});
		void load();
	}

	if (loading)
		return (
			<PageLayout title="Activity">
				<p className="mt-10 text-sm text-carbon-500">Loading activity…</p>
			</PageLayout>
		);

	if (error)
		return (
			<PageLayout title="Activity">
				<p className="mt-10 text-sm text-lockout">{error}</p>
				<button
					className="mt-4 rounded-control border border-primary px-4 py-2 text-sm"
					onClick={() => void load()}
				>
					Retry
				</button>
			</PageLayout>
		);

	return (
		<PageLayout title="Activity">
			<ActivityIntro />
			<AuditControls
				from={range.from}
				to={range.to}
				onFromChange={(from) => setRange((current) => ({ ...current, from }))}
				onToChange={(to) => setRange((current) => ({ ...current, to }))}
				onRefresh={resetActivity}
			/>
			<div className="mt-8 sm:mt-12" aria-label="Activity by lifecycle">
				<ActivityLifecycleTabs
					sections={sections}
					selectedId={selectedActivity}
					onSelect={setSelectedActivity}
				/>
				{sections.map((section) =>
					section.id === selectedActivity ? (
						<ActivityLifecycle
							key={section.id}
							section={section}
							visibleCount={visibleCounts[section.id] ?? INITIAL_VISIBLE_COUNT}
							onLoadMore={() =>
								setVisibleCounts((current) => ({
									...current,
									[section.id]:
										(current[section.id] ?? INITIAL_VISIBLE_COUNT) + 6,
								}))
							}
						/>
					) : null,
				)}
			</div>
		</PageLayout>
	);
}
