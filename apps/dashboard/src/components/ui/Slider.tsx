export type SliderVariant = 'soft-carbon' | 'safe' | 'caution' | 'lockout';

type SliderProps = {
	value: number;
	onChange: (_value: number) => void;
	min?: number;
	max?: number;
	step?: number;
	ariaLabel: string;
	id?: string;
	disabled?: boolean;
	variant?: SliderVariant;
};

const variantClasses: Record<SliderVariant, { fill: string; range: string }> = {
	'soft-carbon': {
		fill: 'bg-carbon-300',
		range:
			'[&::-moz-range-progress]:rounded-full [&::-moz-range-progress]:bg-carbon-300 [&::-moz-range-thumb]:border-carbon-300 [&::-webkit-slider-thumb]:border-carbon-300',
	},
	safe: {
		fill: 'bg-safe',
		range:
			'[&::-moz-range-progress]:rounded-full [&::-moz-range-progress]:bg-safe [&::-moz-range-thumb]:border-safe [&::-webkit-slider-thumb]:border-safe',
	},
	caution: {
		fill: 'bg-caution',
		range:
			'[&::-moz-range-progress]:rounded-full [&::-moz-range-progress]:bg-caution [&::-moz-range-thumb]:border-caution [&::-webkit-slider-thumb]:border-caution',
	},
	lockout: {
		fill: 'bg-lockout',
		range:
			'[&::-moz-range-progress]:rounded-full [&::-moz-range-progress]:bg-lockout [&::-moz-range-thumb]:border-lockout [&::-webkit-slider-thumb]:border-lockout',
	},
};

export default function Slider({
	value,
	onChange,
	min = 0,
	max = 1,
	step = 0.01,
	ariaLabel,
	id,
	disabled = false,
	variant = 'soft-carbon',
}: SliderProps) {
	const clampedValue = Math.min(max, Math.max(min, value));
	const range = max - min;
	const progress = range === 0 ? 0 : ((clampedValue - min) / range) * 100;
	const colors = variantClasses[variant];

	return (
		<div className="relative flex h-5 items-center">
			<div
				className="pointer-events-none absolute inset-x-0 h-1.5 overflow-hidden rounded-full bg-stone-200"
				aria-hidden="true"
			>
				<div
					className={`h-full rounded-full ${colors.fill}`}
					style={{ width: `${progress}%` }}
				/>
			</div>
			<input
				id={id}
				type="range"
				min={min}
				max={max}
				step={step}
				value={clampedValue}
				onChange={(event) => onChange(Number(event.target.value))}
				aria-label={ariaLabel}
				disabled={disabled}
				className={`relative z-10 h-5 w-full cursor-pointer appearance-none bg-transparent outline-none disabled:cursor-not-allowed disabled:opacity-50 ${colors.range} [&::-moz-range-thumb]:size-4 [&::-moz-range-thumb]:appearance-none [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:border-2 [&::-moz-range-thumb]:bg-paper-50 [&::-moz-range-thumb]:shadow-sm [&::-moz-range-track]:h-1.5 [&::-moz-range-track]:rounded-full [&::-moz-range-track]:bg-transparent [&::-webkit-slider-runnable-track]:h-1.5 [&::-webkit-slider-runnable-track]:rounded-full [&::-webkit-slider-runnable-track]:bg-transparent [&::-webkit-slider-thumb]:-mt-1.25 [&::-webkit-slider-thumb]:size-4 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:bg-paper-50 [&::-webkit-slider-thumb]:shadow-sm`}
			/>
		</div>
	);
}
