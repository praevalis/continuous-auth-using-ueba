import { LuShieldCheck } from 'react-icons/lu';
import SegmentedControl from '@/components/ui/SegmentedControl';
import type { PolicyMode } from './types';

const modeOptions: Array<{ value: PolicyMode; label: string }> = [
	{ value: 'shadow', label: 'Shadow' },
	{ value: 'alert_only', label: 'Alert only' },
	{ value: 'enforce', label: 'Enforce' },
];

type PolicyModeSelectorProps = {
	value: PolicyMode;
	onChange: (_MODE: PolicyMode) => void;
};

export default function PolicyModeSelector({
	value,
	onChange,
}: PolicyModeSelectorProps) {
	return (
		<section
			className="mt-10 border-t border-stone-300 pt-6"
			aria-label="Policy mode"
		>
			<div className="flex min-w-0 flex-col gap-4 sm:flex-row sm:items-center">
				<h2 className="flex items-center gap-3 text-base font-medium text-primary">
					<LuShieldCheck size={24} aria-hidden="true" />
					Mode
				</h2>
				<SegmentedControl
					options={modeOptions}
					selectedValue={value}
					onChange={onChange}
					className="min-w-0 flex-1 sm:max-w-md"
				/>
			</div>
		</section>
	);
}
