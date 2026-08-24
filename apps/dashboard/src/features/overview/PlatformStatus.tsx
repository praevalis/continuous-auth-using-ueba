import type { IconType } from 'react-icons';
import { LuCheck, LuInfo, LuMinus, LuX } from 'react-icons/lu';
import Badge from '@/components/ui/Badge';
import type { OverviewPlatformItem, OverviewTone } from './types';

function statusPresentation(tone: OverviewTone): {
	color: string;
	background: string;
	Icon: IconType;
} {
	if (tone === 'caution') {
		return {
			color: 'text-caution',
			background: 'bg-caution',
			Icon: LuInfo,
		};
	}
	if (tone === 'lockout') {
		return {
			color: 'text-lockout',
			background: 'bg-lockout',
			Icon: LuX,
		};
	}
	if (tone === 'safe') {
		return { color: 'text-safe', background: 'bg-safe', Icon: LuCheck };
	}
	return {
		color: 'text-carbon-500',
		background: 'bg-carbon-300',
		Icon: LuMinus,
	};
}

function StatusBadge({ status, tone }: { status: string; tone: OverviewTone }) {
	const presentation = statusPresentation(tone);
	return (
		<Badge
			className={`text-sm ${presentation.color}`}
			leading={
				<span
					className={`relative block size-4 shrink-0 rounded-full ${presentation.background} text-white`}
				>
					<presentation.Icon
						size={10}
						className="absolute inset-0 m-auto block"
						aria-hidden="true"
					/>
				</span>
			}
		>
			{status}
		</Badge>
	);
}

type PlatformStatusProps = {
	heading: string;
	items: OverviewPlatformItem[];
	loading?: boolean;
};

export default function PlatformStatus({
	heading,
	items,
	loading = false,
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
							<div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
								<StatusBadge status={item.status} tone={item.tone} />
								<span className="text-sm text-carbon-300">
									· {item.updated}
								</span>
							</div>
							{loading && (
								<span className="sr-only">Loading platform status</span>
							)}
						</div>
					</div>
				))}
			</div>
		</section>
	);
}
