import type { IconType } from 'react-icons';
import { LuCheck } from 'react-icons/lu';
import Badge from '@/components/ui/Badge';

type PlatformItem = {
	icon: IconType;
	label: string;
	status: string;
	updated: string;
};
type PlatformStatusProps = { heading: string; items: PlatformItem[] };

export default function PlatformStatus({
	heading,
	items,
}: PlatformStatusProps) {
	return (
		<section
			className="mt-12 rounded-panel bg-stone-100/70 px-5 py-5 sm:px-7 sm:py-6"
			aria-labelledby="platform-status-heading"
		>
			<h2
				id="platform-status-heading"
				className="text-lg font-semibold text-primary"
			>
				{heading}
			</h2>
			<div className="mt-6 grid gap-6 md:grid-cols-3 md:gap-0">
				{items.map((item, index) => (
					<div
						key={item.label}
						className={`relative flex items-center gap-4 md:px-5 ${index > 0 ? 'border-t border-stone-300 pt-6 md:border-l md:border-t-0 md:pt-0' : ''}`}
					>
						<div className="grid size-14 shrink-0 place-items-center rounded-full border border-primary text-primary">
							<item.icon size={28} />
						</div>
						<div>
							<h3 className="font-medium text-primary">{item.label}</h3>
							<Badge
								className="mt-1 text-sm text-safe"
								leading={
									<span className="grid size-4 place-items-center rounded-full bg-safe text-white">
										<LuCheck size={10} />
									</span>
								}
							>
								{item.status}
							</Badge>
							<span className="ml-2 text-sm text-carbon-300">
								· {item.updated}
							</span>
						</div>
					</div>
				))}
			</div>
		</section>
	);
}
