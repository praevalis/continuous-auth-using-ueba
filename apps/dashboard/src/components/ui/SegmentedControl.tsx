import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';

export type SegmentedControlOption<T extends string> = {
	value: T;
	label: ReactNode;
};

type SegmentedControlProps<T extends string> = {
	options: SegmentedControlOption<T>[];
	selectedValue: T;
	onChange: (_value: T) => void;
	className?: string;
};

export default function SegmentedControl<T extends string>({
	options,
	selectedValue,
	onChange,
	className,
}: SegmentedControlProps<T>) {
	return (
		<div
			className={cn(
				'grid overflow-hidden rounded-control border border-stone-300',
				className,
			)}
			style={{
				gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))`,
			}}
			role="group"
		>
			{options.map((option) => {
				const isSelected = option.value === selectedValue;
				return (
					<button
						key={option.value}
						type="button"
						className={cn(
							'min-h-10 whitespace-nowrap border-r border-stone-300 px-2 text-xs last:border-r-0 sm:text-sm',
							isSelected
								? 'border-b-2 border-b-primary bg-primary-soft font-semibold text-primary'
								: 'text-carbon-700 hover:bg-stone-100',
						)}
						onClick={() => onChange(option.value)}
						aria-pressed={isSelected}
					>
						{option.label}
					</button>
				);
			})}
		</div>
	);
}
