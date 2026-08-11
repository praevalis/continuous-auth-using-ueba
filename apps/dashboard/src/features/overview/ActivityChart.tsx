type ActivityTrace = { path: string; color: string };
type ActivityChartProps = {
	heading: string;
	traces: ActivityTrace[];
	labels: string[];
	ariaLabel: string;
};

export default function ActivityChart({
	heading,
	traces,
	labels,
	ariaLabel,
}: ActivityChartProps) {
	return (
		<div className="mt-4">
			<p className="text-sm font-medium text-carbon-700">{heading}</p>
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
			<div className="flex justify-between text-xs text-carbon-300">
				{labels.map((label) => (
					<span key={label}>{label}</span>
				))}
			</div>
		</div>
	);
}
