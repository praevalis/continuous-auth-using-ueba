import RankedList from '@/components/ui/RankedList';
import { useNavigate } from 'react-router-dom';
import type { OverviewReviewItem } from './types';

export default function WorkToReview({
	heading,
	items,
	loading = false,
}: {
	heading: string;
	items: OverviewReviewItem[];
	loading?: boolean;
}) {
	const navigate = useNavigate();

	return (
		<section aria-labelledby="review-heading">
			<h2 id="review-heading" className="text-lg font-semibold">
				{heading}
			</h2>
			<div className="mt-4">
				{loading ? (
					<div className="divide-y divide-stone-300/80">
						{items.map((item) => (
							<div
								className="grid min-h-12 grid-cols-[auto_1fr_auto_auto] items-center gap-4 py-3 text-sm"
								key={item.id}
							>
								<span>{item.id}</span>
								<span>{item.label}</span>
								<span className="h-4 w-5 animate-pulse rounded bg-stone-200" />
								<span aria-hidden="true">›</span>
							</div>
						))}
					</div>
				) : (
					<RankedList items={items} onItemClick={() => navigate('/activity')} />
				)}
			</div>
		</section>
	);
}
