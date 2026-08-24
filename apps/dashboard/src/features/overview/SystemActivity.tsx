import Timeline, { type TimelineItem } from '@/components/ui/Timeline';

export default function SystemActivity({
	heading,
	items,
	loading = false,
}: {
	heading: string;
	items: TimelineItem[];
	loading?: boolean;
}) {
	return (
		<section className="mt-12" aria-labelledby="system-heading">
			<h2 id="system-heading" className="text-lg font-semibold">
				{heading}
			</h2>
			<div className="mt-5">
				{loading ? (
					<div className="flex flex-col gap-4 md:flex-row">
						{Array.from({ length: 4 }, (_, index) => (
							<div className="flex flex-1 items-start gap-3" key={index}>
								<span className="size-12 shrink-0 animate-pulse rounded-full bg-stone-200" />
								<span className="space-y-2 pt-1">
									<span className="block h-4 w-28 animate-pulse rounded bg-stone-200" />
									<span className="block h-3 w-20 animate-pulse rounded bg-stone-200" />
								</span>
							</div>
						))}
					</div>
				) : items.length > 0 ? (
					<Timeline items={items} />
				) : (
					<p className="text-sm text-carbon-500">No recent system activity.</p>
				)}
			</div>
		</section>
	);
}
