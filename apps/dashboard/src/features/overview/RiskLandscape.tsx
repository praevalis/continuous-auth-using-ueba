import type { ComponentProps } from 'react';
import SegmentedBar from '@/components/ui/SegmentedBar';
import ActivityChart from './ActivityChart';

type RiskSegment = {
	label: string;
	value: string;
	className: string;
	tone: string;
};
type RiskLandscapeProps = {
	heading: string;
	segments: RiskSegment[];
	chart: ComponentProps<typeof ActivityChart>;
};

export default function RiskLandscape({
	heading,
	segments,
	chart,
}: RiskLandscapeProps) {
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
					<SegmentedBar items={segments} />
				</div>
				<div className="mt-2 flex justify-between text-sm font-medium">
					{segments.map((segment) => (
						<span key={segment.label} className={segment.tone}>
							{segment.value}
						</span>
					))}
				</div>
				<div className="mt-4 grid grid-cols-3 gap-3 text-sm">
					{segments.map((segment) => (
						<span className="flex items-center gap-2" key={segment.label}>
							<span className={`size-2.5 ${segment.className}`} />
							{segment.label}&nbsp; {segment.value}
						</span>
					))}
				</div>
			</div>
			<ActivityChart {...chart} />
		</section>
	);
}
