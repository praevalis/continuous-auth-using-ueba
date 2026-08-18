import type { ThreatEvent, ThreatFeedFilters } from './types';

export function filterThreatEvents(
	events: ThreatEvent[],
	{ search, result, risk }: ThreatFeedFilters,
) {
	const normalizedSearch = search.trim().toLowerCase();

	return events.filter((event) => {
		const matchesSearch = `${event.user} ${event.id}`
			.toLowerCase()
			.includes(normalizedSearch);
		const matchesResult =
			result === 'all' || event.result.toLowerCase() === result;
		const matchesRisk = risk === 'all' || event.tone === risk;

		return matchesSearch && matchesResult && matchesRisk;
	});
}

export function paginateThreatEvents(
	events: ThreatEvent[],
	visibleCount: number,
) {
	return {
		events: events.slice(0, visibleCount),
		hasMore: events.length > visibleCount,
	};
}
