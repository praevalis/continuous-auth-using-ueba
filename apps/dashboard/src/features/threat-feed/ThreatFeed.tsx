import { useMemo, useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import ThreatFeedIntro from './ThreatFeedIntro';
import ThreatFeedSignals from './ThreatFeedSignals';
import ThreatLedger from './ThreatLedger';
import EventDetail from './EventDetail';
import ThreatFeedToolbar from './ThreatFeedToolbar';
import { mockThreatEvents } from './mock-data';
import { filterThreatEvents, paginateThreatEvents } from './selectors';
import type { ThreatFeedFilters } from './types';

const INITIAL_PAGE_SIZE = 10;

export default function ThreatFeed() {
	const [selectedId, setSelectedId] = useState<string | null>('evt-002');
	const [filters, setFilters] = useState<ThreatFeedFilters>({
		search: '',
		result: 'all',
		risk: 'all',
	});
	const [visibleCount, setVisibleCount] = useState(INITIAL_PAGE_SIZE);

	const filteredEvents = useMemo(
		() => filterThreatEvents(mockThreatEvents, filters),
		[filters],
	);
	const { events: loadedEvents, hasMore } = useMemo(
		() => paginateThreatEvents(filteredEvents, visibleCount),
		[filteredEvents, visibleCount],
	);
	const selectedEvent =
		mockThreatEvents.find((event) => event.id === selectedId) ??
		mockThreatEvents[0];

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
			<ThreatFeedSignals />
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
							onRefresh={() => setVisibleCount(INITIAL_PAGE_SIZE)}
						/>
					}
					events={loadedEvents}
					selectedId={selectedId}
					onSelect={(id) =>
						setSelectedId((currentId) => (currentId === id ? null : id))
					}
					hasMore={hasMore}
					onLoadMore={() =>
						setVisibleCount((count) => count + INITIAL_PAGE_SIZE)
					}
				/>
				<EventDetail event={selectedEvent} />
			</div>
		</PageLayout>
	);
}
