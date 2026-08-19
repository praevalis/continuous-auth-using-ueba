import { useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import ActivityIntro from './ActivityIntro';
import AuditControls from './AuditControls';
import ActivityLifecycle from './ActivityLifecycle';
import ActivityLifecycleTabs from './ActivityLifecycleTabs';
import { mockActivitySections } from './mock-data';
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

function getInitialVisibleCounts() {
	return Object.fromEntries(
		mockActivitySections.map((section) => [section.id, INITIAL_VISIBLE_COUNT]),
	) as Record<ActivityKind, number>;
}

export default function Activity() {
	const [range, setRange] = useState(getInitialDateRange);
	const [selectedActivity, setSelectedActivity] =
		useState<ActivityKind>('analysis');
	const [visibleCounts, setVisibleCounts] = useState(getInitialVisibleCounts);

	function resetActivity() {
		setVisibleCounts(getInitialVisibleCounts());
	}

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
					sections={mockActivitySections}
					selectedId={selectedActivity}
					onSelect={setSelectedActivity}
				/>
				{mockActivitySections.map((section) =>
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
