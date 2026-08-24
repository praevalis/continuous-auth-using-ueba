import { LuChevronDown, LuChevronRight } from 'react-icons/lu';
import type { ReactNode } from 'react';
import Badge from '@/components/ui/Badge';
import ScrollableArea from '@/components/ui/ScrollableArea';
import ResourceError from '@/components/ui/ResourceError';
import Button from '@/components/ui/Button';
import type { ThreatEvent } from './types';
import EventDetail from './EventDetail';
import { formatTimestamp } from '@/utils';

function toneClass(tone: ThreatEvent['tone']) {
	return tone === 'safe'
		? 'text-safe'
		: tone === 'caution'
			? 'text-caution'
			: tone === 'lockout'
				? 'text-lockout'
				: 'text-carbon-300';
}

function toneBackground(tone: ThreatEvent['tone']) {
	return tone === 'safe'
		? 'bg-safe'
		: tone === 'caution'
			? 'bg-caution'
			: tone === 'lockout'
				? 'bg-lockout'
				: 'bg-stone-300';
}

function RiskBadge({ event }: { event: ThreatEvent }) {
	return (
		<Badge
			className={`text-xs ${toneClass(event.tone)}`}
			leading={
				<span className={`size-2 rounded-full ${toneBackground(event.tone)}`} />
			}
		>
			{event.risk}
		</Badge>
	);
}

function ScoreTrace({ event }: { event: ThreatEvent }) {
	const color =
		event.tone === 'safe'
			? '#667A68'
			: event.tone === 'caution'
				? '#A87528'
				: '#984A43';
	const marker = event.score === null ? null : 18 + event.score * 58;
	return (
		<div className="min-w-24">
			<span className="font-mono text-xs">
				{event.score === null ? '—' : event.score.toFixed(3)}
			</span>
			<svg
				className="mt-1 h-5 w-24"
				viewBox="0 0 80 20"
				preserveAspectRatio="none"
				aria-label={`Score trace for ${event.user}`}
				role="img"
			>
				<path
					d="M0 12 C5 9 7 15 12 11 S19 14 24 10 S31 13 36 11 S43 14 48 10 S55 13 60 11 S67 14 72 10 S77 12 80 9"
					fill="none"
					stroke={color}
					strokeWidth="1.5"
				/>
				{marker !== null && (
					<circle
						cx={marker}
						cy="11"
						r="2.5"
						fill="white"
						stroke={color}
						strokeWidth="1.5"
					/>
				)}
			</svg>
		</div>
	);
}

function Identity({
	event,
	mobile = false,
}: {
	event: ThreatEvent;
	mobile?: boolean;
}) {
	return (
		<span className="flex min-w-0 items-center gap-2">
			<span className="grid size-7 shrink-0 place-items-center rounded-full bg-stone-100 text-xs">
				{event.initials}
			</span>
			<span className="min-w-0">
				<span
					className={`block text-xs ${mobile ? 'whitespace-nowrap text-[0.6875rem]' : 'truncate'}`}
				>
					{event.user}
				</span>
				<span
					className={`block text-xs text-carbon-300 ${mobile ? 'whitespace-nowrap text-[0.6875rem]' : 'truncate'}`}
				>
					{event.device} · {event.network}
				</span>
			</span>
		</span>
	);
}

function DesktopEventRowSkeleton() {
	return (
		<div
			className="relative grid w-full grid-cols-[72px_minmax(150px,1.4fr)_minmax(90px,0.9fr)_100px_110px_minmax(130px,1fr)] items-center gap-4 py-3 pl-4 pr-2"
			aria-hidden="true"
		>
			<span className="absolute inset-y-3 left-0 w-1 rounded-full bg-stone-200" />
			<span className="h-3 w-16 animate-pulse rounded bg-stone-200" />
			<span className="flex min-w-0 items-center gap-2">
				<span className="size-7 shrink-0 animate-pulse rounded-full bg-stone-200" />
				<span className="min-w-0 flex-1 space-y-1.5">
					<span className="block h-3 w-24 animate-pulse rounded bg-stone-200" />
					<span className="block h-2.5 w-32 animate-pulse rounded bg-stone-200" />
				</span>
			</span>
			<span className="h-3 w-20 animate-pulse rounded bg-stone-200" />
			<span className="h-5 w-16 animate-pulse rounded-control bg-stone-200" />
			<span className="space-y-1.5">
				<span className="block h-3 w-12 animate-pulse rounded bg-stone-200" />
				<span className="block h-2 animate-pulse rounded bg-stone-200" />
			</span>
			<span className="h-3 w-28 animate-pulse rounded bg-stone-200" />
		</div>
	);
}

function MobileEventRowSkeleton() {
	return (
		<div
			className="relative grid w-full grid-cols-[58px_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)_16px] grid-rows-[minmax(0,1fr)_auto] gap-x-2 gap-y-2 px-3 py-3"
			aria-hidden="true"
		>
			<span className="absolute inset-y-3 left-0 w-1 rounded-full bg-stone-200" />
			<span className="col-start-1 row-start-1 h-3 w-12 animate-pulse self-center rounded bg-stone-200" />
			<span className="col-start-2 col-span-3 row-start-1 flex items-center gap-2">
				<span className="size-7 shrink-0 animate-pulse rounded-full bg-stone-200" />
				<span className="min-w-0 flex-1 space-y-1.5">
					<span className="block h-3 w-24 animate-pulse rounded bg-stone-200" />
					<span className="block h-2.5 w-32 animate-pulse rounded bg-stone-200" />
				</span>
			</span>
			<span className="col-start-5 row-start-1 row-span-2 h-4 w-3 animate-pulse self-center rounded bg-stone-200" />
			<span className="col-start-2 col-span-3 row-start-2 grid grid-cols-3 gap-2">
				<span className="h-3 w-12 animate-pulse rounded bg-stone-200" />
				<span className="h-3 w-14 animate-pulse rounded bg-stone-200" />
				<span className="h-3 w-16 animate-pulse rounded bg-stone-200" />
			</span>
		</div>
	);
}

function FeedError({
	error,
	onRetry,
	className,
}: {
	error: Error;
	onRetry: () => void;
	className: string;
}) {
	return (
		<ResourceError
			title="Unable to load threat feed"
			error={error}
			onRetry={onRetry}
			className={className}
		/>
	);
}

function DesktopEventRow({
	event,
	selected,
	onSelect,
}: {
	event: ThreatEvent;
	selected: boolean;
	onSelect: () => void;
}) {
	return (
		<Button
			variant="quiet"
			onClick={onSelect}
			className={`group relative grid w-full min-h-0 grid-cols-[72px_minmax(150px,1.4fr)_minmax(90px,0.9fr)_100px_110px_minmax(130px,1fr)] gap-4 rounded-none px-0 py-3 pl-4 pr-2 text-left text-xs transition-colors hover:bg-primary-soft/50 ${selected ? 'bg-primary-soft/70' : 'bg-transparent'}`}
		>
			<span
				className={`absolute inset-y-3 left-0 w-1 rounded-full ${toneBackground(event.tone)}`}
			/>
			<time
				className="font-mono text-xs text-carbon-700"
				dateTime={event.dateTime}
			>
				{event.time}
			</time>
			<Identity event={event} />
			<span>{event.signInType}</span>
			<RiskBadge event={event} />
			<ScoreTrace event={event} />
			<span className="flex items-center justify-between gap-2">
				<span>{event.response}</span>
				<LuChevronRight className="shrink-0 text-carbon-300" size={16} />
			</span>
		</Button>
	);
}

function MobileEventRow({
	event,
	selected,
	onSelect,
}: {
	event: ThreatEvent;
	selected: boolean;
	onSelect: () => void;
}) {
	return (
		<Button
			variant="quiet"
			onClick={onSelect}
			className={`relative grid w-full min-h-0 grid-cols-[58px_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)_16px] grid-rows-[minmax(0,1fr)_auto] gap-x-2 gap-y-2 rounded-none px-3 py-3 text-left text-xs ${selected ? 'bg-primary-soft/70' : 'bg-transparent'}`}
		>
			<span
				className={`absolute inset-y-3 left-0 w-1 rounded-full ${toneBackground(event.tone)}`}
			/>
			<span className="col-start-1 row-start-1 self-center font-mono text-xs text-carbon-700">
				{event.time}
			</span>
			<span className="col-start-2 row-start-1 col-span-3 min-w-0 self-center">
				<Identity event={event} mobile />
			</span>
			<LuChevronRight
				className="col-start-5 row-start-1 row-span-2 self-center text-carbon-300"
				size={16}
			/>
			<span className="col-start-2 row-start-2 col-span-3 grid min-w-0 grid-cols-3 items-center gap-2">
				<span className="min-w-0 font-mono text-xs">
					{event.score === null ? '—' : event.score.toFixed(3)}
				</span>
				<span
					className={`min-w-0 text-xs ${event.result === 'Failed' ? 'text-lockout' : 'text-safe'}`}
				>
					{event.result}
				</span>
				<RiskBadge event={event} />
			</span>
		</Button>
	);
}

export default function ThreatLedger({
	toolbar,
	events,
	loading,
	error,
	onRetry,
	selectedId,
	selectedEventDetail,
	onSelect,
	hasMore,
	onLoadMore,
	totalCount,
	updatedAt,
}: {
	toolbar: ReactNode;
	events: ThreatEvent[];
	loading: boolean;
	error: Error | null;
	onRetry: () => void;
	selectedId: string | null;
	selectedEventDetail?: ThreatEvent;
	onSelect: (_id: string) => void;
	hasMore: boolean;
	onLoadMore: () => void;
	totalCount: number;
	updatedAt: string | null;
}) {
	const updatedLabel = updatedAt
		? `Updated ${formatTimestamp(updatedAt)}`
		: '—';
	return (
		<section
			className="min-w-0 max-w-full overflow-hidden"
			aria-labelledby="live-threat-feed-heading"
		>
			{toolbar}
			<div className="flex items-baseline justify-start gap-4">
				<h2
					id="live-threat-feed-heading"
					className="text-lg font-semibold text-primary"
				>
					Live threat feed
				</h2>
				<span className="text-xs text-carbon-300">{updatedLabel}</span>
			</div>
			<div className="mt-6 hidden border-b border-stone-300 pb-2 text-left text-xs font-medium text-carbon-700 lg:grid lg:grid-cols-[72px_minmax(150px,1.4fr)_minmax(90px,0.9fr)_100px_110px_minmax(130px,1fr)] lg:gap-4 lg:pl-4">
				<span>Occurred</span>
				<span>User</span>
				<span>Sign-in type</span>
				<span>Risk level</span>
				<span>Score</span>
				<span>Response decision</span>
			</div>
			<ScrollableArea className="hidden h-[41rem] divide-y divide-stone-300/80 lg:block">
				{loading ? (
					Array.from({ length: 6 }, (_, index) => (
						<DesktopEventRowSkeleton key={index} />
					))
				) : error ? (
					<FeedError
						error={error}
						onRetry={onRetry}
						className="flex h-full flex-col items-start justify-center px-4 text-sm text-lockout"
					/>
				) : (
					events.map((event) => (
						<DesktopEventRow
							key={event.id}
							event={event}
							selected={event.id === selectedId}
							onSelect={() => onSelect(event.id)}
						/>
					))
				)}
			</ScrollableArea>
			<div className="mt-6 space-y-3 lg:hidden">
				{loading ? (
					Array.from({ length: 4 }, (_, index) => (
						<div
							key={index}
							className="overflow-hidden rounded-panel border border-stone-300 bg-transparent"
						>
							<MobileEventRowSkeleton />
						</div>
					))
				) : error ? (
					<FeedError
						error={error}
						onRetry={onRetry}
						className="rounded-panel border border-stone-300 px-3 py-6 text-sm text-lockout"
					/>
				) : (
					events.map((event) => (
						<div
							key={event.id}
							className="overflow-hidden rounded-panel border border-stone-300 bg-transparent"
						>
							<MobileEventRow
								event={event}
								selected={event.id === selectedId}
								onSelect={() => onSelect(event.id)}
							/>
							{event.id === selectedId && (
								<EventDetail event={selectedEventDetail ?? event} mobile />
							)}
						</div>
					))
				)}
			</div>
			<div className="mt-5 flex items-center justify-between border-t border-stone-300 pt-3 text-xs font-medium text-carbon-700">
				<span>
					{events.length ? `Showing 1–${events.length}` : 'No events'} of{' '}
					{totalCount.toLocaleString()} events
				</span>
				{hasMore && (
					<Button
						onClick={onLoadMore}
						variant="quiet"
						size="sm"
						trailing={<LuChevronDown size={15} aria-hidden="true" />}
						className="min-h-0 px-0 py-0 text-xs font-medium text-carbon-700 hover:bg-transparent hover:text-primary"
					>
						Load more
					</Button>
				)}
			</div>
		</section>
	);
}
