type RankedListItem = {
	id: string;
	label: string;
	value: string;
};

type RankedListProps = {
	items: RankedListItem[];
};

export default function RankedList({ items }: RankedListProps) {
	return (
		<div className="divide-y divide-stone-300/80">
			{items.map((item) => (
				<div
					className="grid min-h-12 grid-cols-[auto_1fr_auto_auto] items-center gap-4 py-3 text-sm"
					key={item.id}
				>
					<span className="font-semibold text-primary">{item.id}</span>
					<span>{item.label}</span>
					<span>{item.value}</span>
					<span aria-hidden="true">›</span>
				</div>
			))}
		</div>
	);
}
