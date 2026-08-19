import type { ActivitySection } from './types';
import { LuChevronDown } from 'react-icons/lu';

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
	time,
	title,
	user,
	status,
	statusTone,
}: ActivitySection['entries'][number]) {
	return (
		<li className="grid min-h-16 grid-cols-[5.5rem_minmax(0,1fr)_auto] items-center gap-2 border-b border-stone-300/80 py-2 text-sm last:border-b-0 sm:grid-cols-[6rem_minmax(0,1fr)_auto]">
			<time className="font-mono text-xs text-carbon-500 sm:text-sm">
				{time}
			</time>
			<div className="min-w-0">
				<p className="truncate text-sm text-primary">{title}</p>
				<p className="truncate text-xs text-carbon-300">{user}</p>
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
					{visibleEntries.map((entry) => (
						<ActivityEntry key={entry.id} {...entry} />
					))}
				</ul>
				<div className="mt-5 flex items-center justify-between border-t border-stone-300 pt-3 text-xs font-medium text-carbon-700">
					<span>
						Showing 1–{visibleEntries.length} of {section.entries.length}{' '}
						activities
					</span>
					{hasMore && (
						<button
							type="button"
							onClick={onLoadMore}
							className="inline-flex items-center gap-2 text-xs font-medium text-carbon-700 hover:text-primary"
						>
							Load more <LuChevronDown size={15} />
						</button>
					)}
				</div>
			</div>
		</section>
	);
}
