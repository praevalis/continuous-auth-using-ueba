import type { IconType } from 'react-icons';
import { cn } from '@/utils/cn';

export type TimelineItem = {
	id: string;
	icon: IconType;
	label: string;
	time: string;
	meta: string;
};

type TimelineProps = {
	items: TimelineItem[];
};

export default function Timeline({ items }: TimelineProps) {
	return (
		<div className="flex flex-col md:flex-row">
			{items.map((item, index) => (
				<div
					className={cn(
						'relative flex flex-1 items-start gap-3 py-4 first:pt-0 last:pb-0 md:px-4 md:py-0',
						index > 0 &&
							'border-t border-stone-300 md:border-l md:border-t-0 md:pl-6',
					)}
					key={item.id}
				>
					<div className="grid size-12 shrink-0 place-items-center rounded-full border border-primary text-primary">
						<item.icon size={24} />
					</div>
					<div>
						<p className="font-medium">{item.label}</p>
						<p className="font-mono text-xs">{item.time}</p>
						<p className="text-xs text-carbon-300">{item.meta}</p>
					</div>
				</div>
			))}
		</div>
	);
}
