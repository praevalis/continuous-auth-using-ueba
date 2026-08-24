import { useMemo, useState } from 'react';
import { useTenant } from '@/hooks/useTenant';
import PageLayout from '@/components/layout/PageLayout';
import { useThreatFeed, useThreatFeedEvent } from '@/hooks';
import ResourceError from '@/components/ui/ResourceError';
import ThreatFeedIntro from './ThreatFeedIntro';
import ThreatFeedSignals from './ThreatFeedSignals';
import ThreatLedger from './ThreatLedger';
import EventDetail from './EventDetail';
import ThreatFeedToolbar from './ThreatFeedToolbar';
import { filterThreatEvents, paginateThreatEvents } from './selectors';
import { mapThreatEvent } from './adapters';
import type { ThreatFeedFilters } from './types';
import type { ThreatFeedTimeRange } from '@/hooks/useThreatFeed';

const INITIAL_PAGE_SIZE = 10;

export default function ThreatFeed() {
	const { tenant } = useTenant();
	const [selectedId, setSelectedId] = useState<string | null>(null);
	const [timeRange, setTimeRange] = useState<ThreatFeedTimeRange>('24h');
	const [filters, setFilters] = useState<ThreatFeedFilters>({
		search: '',
		result: 'all',
		risk: 'all',
	});
	const [visibleCount, setVisibleCount] = useState(INITIAL_PAGE_SIZE);
	const feed = useThreatFeed(tenant?.id, timeRange);
	const events = useMemo(() => {
		if (!feed.data) return [];
		const decisions = new Map(
			feed.data.decisions.items.map((decision) => [
				decision.auth_event_id,
				decision,
			]),
		);
		return feed.data.events.items.map((event) =>
			mapThreatEvent(event, decisions.get(event.id)),
		);
	}, [feed.data]);
	const filteredEvents = useMemo(
		() => filterThreatEvents(events, filters),
		[events, filters],
	);
	const { events: loadedEvents, hasMore } = useMemo(
		() => paginateThreatEvents(filteredEvents, visibleCount),
		[filteredEvents, visibleCount],
	);
	const selectedEvent = events.find((event) => event.id === selectedId);
	const selectedEventResource = useThreatFeedEvent(
		tenant?.id,
		selectedEvent?.id,
	);
	const selectedEventDetail = selectedEventResource.data
		? mapThreatEvent(
				selectedEventResource.data.event,
				selectedEventResource.data.policy_decision ?? undefined,
				selectedEventResource.data,
			)
		: selectedEvent;

	function updateFilter<Key extends keyof ThreatFeedFilters>(
		key: Key,
		value: ThreatFeedFilters[Key],
	) {
		setFilters((current) => ({ ...current, [key]: value }));
		setVisibleCount(INITIAL_PAGE_SIZE);
	}

	return (
		<PageLayout title="Threat feed">
			<ThreatFeedIntro />
			<ThreatFeedSignals
				summary={feed.data?.summary ?? null}
				updatedAt={feed.data?.summary.generated_at ?? null}
			/>
			<div className="mt-10 grid gap-10 lg:grid-cols-[minmax(0,1.7fr)_minmax(320px,0.8fr)]">
				<ThreatLedger
					toolbar={
						<ThreatFeedToolbar
							search={filters.search}
							onSearchChange={(value) => updateFilter('search', value)}
							result={filters.result}
							onResultChange={(value) => updateFilter('result', value)}
							risk={filters.risk}
							onRiskChange={(value) => updateFilter('risk', value)}
							timeRange={timeRange}
							onTimeRangeChange={(value) => {
								setTimeRange(value as ThreatFeedTimeRange);
								setVisibleCount(INITIAL_PAGE_SIZE);
							}}
							onRefresh={() => {
								setVisibleCount(INITIAL_PAGE_SIZE);
								void feed.refresh();
							}}
						/>
					}
					events={loadedEvents}
					loading={feed.loading}
					error={feed.error}
					onRetry={() => void feed.refresh()}
					selectedId={selectedId}
					selectedEventDetail={selectedEventDetail}
					onSelect={(id) =>
						setSelectedId((currentId) => (currentId === id ? null : id))
					}
					hasMore={hasMore}
					totalCount={feed.data?.events.pagination.total_count ?? 0}
					updatedAt={feed.data?.summary.generated_at ?? null}
					onLoadMore={() =>
						setVisibleCount((count) => count + INITIAL_PAGE_SIZE)
					}
				/>
				{selectedEventDetail ? (
					selectedEventResource.loading ? (
						<aside className="hidden border-l border-stone-300 pl-6 text-sm text-carbon-500 lg:block">
							Loading event evidence…
						</aside>
					) : selectedEventResource.error ? (
						<ResourceError
							title="Unable to load event evidence"
							error={selectedEventResource.error}
							onRetry={() => void selectedEventResource.refresh()}
							className="hidden min-h-full rounded-none border-0 border-l border-stone-300 bg-transparent px-0 py-0 pl-6 lg:block"
						/>
					) : (
						<EventDetail event={selectedEventDetail} />
					)
				) : (
					<aside className="hidden border-l border-stone-300 pl-6 text-sm text-carbon-500 lg:block">
						Select a sign-in event to review its evidence.
					</aside>
				)}
			</div>
		</PageLayout>
	);
}
