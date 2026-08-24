import type { ActivitySection } from './types';
import type { ActivityKind } from './types';
import { LuChevronDown } from 'react-icons/lu';
import Button from '@/components/ui/Button';

const toneClasses = {
	safe: 'bg-safe',
	caution: 'bg-caution',
	lockout: 'bg-lockout',
	neutral: 'bg-carbon-300',
};

const statusClasses = {
	safe: 'border-safe/40 text-safe',
	caution: 'border-caution/40 text-caution',
	lockout: 'border-lockout/40 text-lockout',
	neutral: 'border-stone-300 text-carbon-500',
};

function ActivityEntry({
	dateTime,
	time,
	title,
	context,
	status,
	statusTone,
}: ActivitySection['entries'][number]) {
	return (
		<li className="grid min-h-16 grid-cols-[58px_minmax(0,1fr)_auto] items-center gap-2 border-b border-stone-300/80 py-2 text-sm last:border-b-0 sm:grid-cols-[72px_minmax(0,1fr)_auto]">
			<time
				dateTime={dateTime}
				className="font-mono text-[0.625rem] leading-tight text-carbon-500 sm:text-xs"
			>
				{time}
			</time>
			<div className="min-w-0">
				<p className="truncate text-sm text-primary">{title}</p>
				<p className="truncate text-xs text-carbon-300">{context}</p>
			</div>
			<span
				className={`max-w-40 truncate rounded-control border px-2 py-1 text-right text-xs ${statusClasses[statusTone]}`}
			>
				{status}
			</span>
		</li>
	);
}

function ActivityStats({ items }: { items: ActivitySection['statItems'] }) {
	return (
		<div className="flex flex-wrap items-center gap-x-8 gap-y-2 border-b border-stone-300 py-3 text-xs text-carbon-500">
			{items.map((item) => (
				<div key={item.label} className="flex min-w-0 items-center gap-2">
					<span
						className={`size-2 shrink-0 rounded-full ${toneClasses[item.tone]}`}
						aria-hidden="true"
					/>
					<span className="font-mono text-primary">{item.value}</span>
					<span className="truncate">{item.label}</span>
				</div>
			))}
		</div>
	);
}

export default function ActivityLifecycle({
	section,
	visibleCount,
	onLoadMore,
}: {
	section: ActivitySection;
	visibleCount: number;
	onLoadMore: () => void;
}) {
	const visibleEntries = section.entries.slice(0, visibleCount);
	const hasMore = visibleEntries.length < section.entries.length;

	return (
		<section
			id={`${section.id}-activity-panel`}
			role="tabpanel"
			aria-labelledby={`${section.id}-activity-tab`}
			tabIndex={0}
			className="min-w-0"
		>
			<div>
				<ActivityStats items={section.statItems} />
				<ul
					className={`mt-2 ${visibleEntries.length > 6 ? 'threat-feed-scrollbar max-h-[24rem] overflow-y-auto [scrollbar-color:theme(colors.primary.soft)_transparent] [scrollbar-width:thin] [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-primary-soft [&::-webkit-scrollbar-track]:bg-transparent' : ''}`}
					aria-label={`${section.title} activity`}
				>
					{visibleEntries.length > 0 ? (
						visibleEntries.map((entry) => (
							<ActivityEntry key={entry.id} {...entry} />
						))
					) : (
						<li className="py-12 text-center text-sm text-carbon-300">
							No activity recorded for this period.
						</li>
					)}
				</ul>
				<div className="mt-5 flex items-center justify-between border-t border-stone-300 pt-3 text-xs font-medium text-carbon-700">
					<span>
						{section.entries.length === 0
							? 'No activities in selected range'
							: `Showing 1–${visibleEntries.length} of ${section.entries.length} activities`}
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
			</div>
		</section>
	);
}

export function ActivityLifecycleSkeleton({
	sectionId = 'analysis',
}: {
	sectionId?: ActivityKind;
}) {
	return (
		<section
			id={`${sectionId}-activity-panel`}
			role="tabpanel"
			aria-labelledby={`${sectionId}-activity-tab`}
			aria-busy="true"
			className="min-w-0"
		>
			<div className="border-b border-stone-300 py-3">
				<div className="h-4 w-40 animate-pulse rounded bg-stone-200" />
			</div>
			<ul className="mt-2" aria-label="Loading activity">
				{Array.from({ length: 6 }, (_, index) => (
					<li
						key={index}
						className="grid min-h-16 grid-cols-[58px_minmax(0,1fr)_auto] items-center gap-2 border-b border-stone-300/80 py-2 sm:grid-cols-[72px_minmax(0,1fr)_auto]"
					>
						<div className="h-3 w-16 animate-pulse rounded bg-stone-200" />
						<div className="min-w-0 space-y-2">
							<div className="h-4 w-48 max-w-full animate-pulse rounded bg-stone-200" />
							<div className="h-3 w-28 animate-pulse rounded bg-stone-200" />
						</div>
						<div className="h-6 w-20 animate-pulse rounded-control bg-stone-200" />
					</li>
				))}
			</ul>
			<div className="mt-5 h-4 w-44 animate-pulse rounded bg-stone-200" />
		</section>
	);
}
