import type { OverviewActivityTrace } from './types';

type ActivityChartProps = {
	heading: string;
	traces: OverviewActivityTrace[];
	labels: string[];
	ariaLabel: string;
	loading?: boolean;
};

export default function ActivityChart({
	heading,
	traces,
	labels,
	ariaLabel,
	loading = false,
}: ActivityChartProps) {
	return (
		<div className="mt-4">
			<p className="text-sm font-medium text-carbon-700">{heading}</p>
			{loading ? (
				<div className="mt-3 h-12 animate-pulse rounded bg-stone-100" />
			) : traces.length > 0 ? (
				<svg
					className="mt-3 h-12 w-full"
					viewBox="0 0 640 48"
					preserveAspectRatio="none"
					aria-label={ariaLabel}
					role="img"
				>
					{traces.map((trace) => (
						<path
							key={`${trace.color}-${trace.path}`}
							d={trace.path}
							stroke={trace.color}
							strokeWidth="2"
							fill="none"
						/>
					))}
				</svg>
			) : (
				<p className="mt-3 h-12 pt-4 text-sm text-carbon-500">
					No recent activity.
				</p>
			)}
			<div className="flex justify-between text-xs text-carbon-300">
				{labels.map((label) => (
					<span key={label}>{label}</span>
				))}
			</div>
		</div>
	);
}
