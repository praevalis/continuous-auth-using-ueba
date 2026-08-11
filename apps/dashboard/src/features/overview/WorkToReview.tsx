import RankedList from '@/components/ui/RankedList';

type ReviewItem = { id: string; label: string; value: string };

export default function WorkToReview({
	heading,
	items,
}: {
	heading: string;
	items: ReviewItem[];
}) {
	return (
		<section aria-labelledby="review-heading">
			<h2 id="review-heading" className="text-lg font-semibold">
				{heading}
			</h2>
			<div className="mt-4">
				<RankedList items={items} />
			</div>
		</section>
	);
}
