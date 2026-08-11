type SegmentedBarItem = {
	label: string;
	value: string;
	className: string;
};

type SegmentedBarProps = {
	items: SegmentedBarItem[];
};

export default function SegmentedBar({ items }: SegmentedBarProps) {
	return (
		<div className="flex gap-2">
			{items.map((item) => (
				<div
					key={item.label}
					className={cn('h-3 rounded-full', item.className)}
					style={{ flex: `0 0 ${item.value}` }}
				/>
			))}
		</div>
	);
}
import { cn } from '@/utils/cn';
