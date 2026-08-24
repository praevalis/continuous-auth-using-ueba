import type { ComponentProps } from 'react';
import SegmentedBar from '@/components/ui/SegmentedBar';
import ActivityChart from './ActivityChart';
import type { OverviewRiskSegment } from './types';

type RiskLandscapeProps = {
	heading: string;
	segments: OverviewRiskSegment[];
	chart: ComponentProps<typeof ActivityChart>;
	loading?: boolean;
};

const EMPTY_SEGMENTS: OverviewRiskSegment[] = [
	{
		label: 'Safe',
		value: '33.333%',
		className: 'bg-safe/30',
		tone: 'text-safe',
	},
	{
		label: 'Caution',
		value: '33.333%',
		className: 'bg-caution/30',
		tone: 'text-caution',
	},
	{
		label: 'Lockout',
		value: '33.333%',
		className: 'bg-lockout/30',
		tone: 'text-lockout',
	},
];

export default function RiskLandscape({
	heading,
	segments,
	chart,
	loading = false,
}: RiskLandscapeProps) {
	const hasRiskActivity = segments.some((segment) => segment.value !== '0%');
	const barSegments = hasRiskActivity ? segments : EMPTY_SEGMENTS;
	return (
		<section
			className="mt-12 grid gap-8 lg:grid-cols-[1.1fr_0.9fr]"
			aria-labelledby="risk-heading"
		>
			<div>
				<h2 id="risk-heading" className="text-lg font-semibold">
					{heading}
				</h2>
				<div className="mt-5">
					<SegmentedBar items={barSegments} />
				</div>
				<div className="mt-2 flex justify-between text-sm font-medium">
					{barSegments.map((segment) => (
						<span key={segment.label} className={segment.tone}>
							{hasRiskActivity ? segment.value : '-'}
						</span>
					))}
				</div>
				<div className="mt-4 grid grid-cols-3 gap-3 text-sm">
					{barSegments.map((segment) => (
						<span className="flex items-center gap-2" key={segment.label}>
							<span className={`size-2.5 ${segment.className}`} />
							{segment.label}&nbsp; {hasRiskActivity ? segment.value : '-'}
						</span>
					))}
				</div>
			</div>
			<ActivityChart {...chart} loading={loading} />
		</section>
	);
}
