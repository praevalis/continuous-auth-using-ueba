type RankedListItem = {
	id: string;
	label: string;
	value: string;
};

type RankedListProps = {
	items: RankedListItem[];
	onItemClick?: (_item: RankedListItem) => void;
};

export default function RankedList({ items, onItemClick }: RankedListProps) {
	return (
		<div className="divide-y divide-stone-300/80">
			{items.map((item) => {
				const className =
					'grid min-h-12 w-full grid-cols-[auto_1fr_auto_auto] items-center gap-4 py-3 text-left text-sm transition hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary';
				const content = (
					<>
						<span className="font-semibold text-primary">{item.id}</span>
						<span>{item.label}</span>
						<span>{item.value}</span>
						<span aria-hidden="true">›</span>
					</>
				);
				return onItemClick ? (
					<button
						type="button"
						className={className}
						key={item.id}
						onClick={() => onItemClick(item)}
						aria-label={`Open activity for ${item.label}`}
					>
						{content}
					</button>
				) : (
					<div className={className} key={item.id}>
						{content}
					</div>
				);
			})}
		</div>
	);
}
