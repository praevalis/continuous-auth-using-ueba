import Timeline, { type TimelineItem } from '@/components/ui/Timeline';

export default function SystemActivity({
	heading,
	items,
}: {
	heading: string;
	items: TimelineItem[];
}) {
	return (
		<section className="mt-12" aria-labelledby="system-heading">
			<h2 id="system-heading" className="text-lg font-semibold">
				{heading}
			</h2>
			<div className="mt-5">
				<Timeline items={items} />
			</div>
		</section>
	);
}
