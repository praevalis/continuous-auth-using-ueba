import { useState } from 'react';
import { useTenant } from '@/hooks/useTenant';
import PageLayout from '@/components/layout/PageLayout';
import ResourceError from '@/components/ui/ResourceError';
import { useActivity } from '@/hooks';
import ActivityIntro from './ActivityIntro';
import AuditControls from './AuditControls';
import ActivityLifecycle, {
	ActivityLifecycleSkeleton,
} from './ActivityLifecycle';
import ActivityLifecycleTabs from './ActivityLifecycleTabs';
import type { ActivitySection } from './types';
import type { ActivityKind } from './types';

const INITIAL_VISIBLE_COUNT = 6;

const activityTabs: Array<Pick<ActivitySection, 'id' | 'title'>> = [
	{ id: 'analysis', title: 'Analysis' },
	{ id: 'decisions', title: 'Alerts' },
	{ id: 'response', title: 'Response activity' },
];

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
	const {
		tenant,
		loading: tenantLoading,
		error: tenantError,
		refresh: refreshTenant,
	} = useTenant();
	const activity = useActivity(tenant?.id, range);
	const sections = activity.data ?? [];
	const [selectedActivity, setSelectedActivity] =
		useState<ActivityKind>('analysis');
	const [visibleCounts, setVisibleCounts] = useState<
		Record<ActivityKind, number>
	>({
		analysis: INITIAL_VISIBLE_COUNT,
		decisions: INITIAL_VISIBLE_COUNT,
		response: INITIAL_VISIBLE_COUNT,
	});

	function resetActivity() {
		setVisibleCounts({
			analysis: INITIAL_VISIBLE_COUNT,
			decisions: INITIAL_VISIBLE_COUNT,
			response: INITIAL_VISIBLE_COUNT,
		});
		if (tenantError) {
			void refreshTenant();
			return;
		}
		void activity.refresh();
	}

	const loading = tenantLoading || activity.loading;
	const error = tenantError ?? activity.error?.message ?? null;

	return (
		<PageLayout title="Activity">
			<ActivityIntro loading={loading} />
			<AuditControls
				from={range.from}
				to={range.to}
				onFromChange={(from) => {
					setVisibleCounts({
						analysis: INITIAL_VISIBLE_COUNT,
						decisions: INITIAL_VISIBLE_COUNT,
						response: INITIAL_VISIBLE_COUNT,
					});
					setRange((current) => ({ ...current, from }));
				}}
				onToChange={(to) => {
					setVisibleCounts({
						analysis: INITIAL_VISIBLE_COUNT,
						decisions: INITIAL_VISIBLE_COUNT,
						response: INITIAL_VISIBLE_COUNT,
					});
					setRange((current) => ({ ...current, to }));
				}}
				onRefresh={resetActivity}
			/>
			<div className="mt-8 sm:mt-12" aria-label="Activity by lifecycle">
				<ActivityLifecycleTabs
					sections={loading || Boolean(error) ? activityTabs : sections}
					selectedId={selectedActivity}
					onSelect={setSelectedActivity}
				/>
				{loading ? (
					<ActivityLifecycleSkeleton sectionId={selectedActivity} />
				) : error ? (
					<ResourceError
						title="Unable to load activity"
						error={error}
						onRetry={resetActivity}
						className="rounded-none border-x-0 border-t-0 border-b border-stone-300 bg-transparent px-0 py-8"
					/>
				) : (
					sections.map((section) =>
						section.id === selectedActivity ? (
							<ActivityLifecycle
								key={section.id}
								section={section}
								visibleCount={
									visibleCounts[section.id] ?? INITIAL_VISIBLE_COUNT
								}
								onLoadMore={() =>
									setVisibleCounts((current) => ({
										...current,
										[section.id]:
											(current[section.id] ?? INITIAL_VISIBLE_COUNT) + 6,
									}))
								}
							/>
						) : null,
					)
				)}
			</div>
		</PageLayout>
	);
}
