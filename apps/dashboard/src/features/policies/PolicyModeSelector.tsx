import { LuShieldCheck } from 'react-icons/lu';
import SegmentedControl from '@/components/ui/SegmentedControl';
import InlineError from '@/components/ui/InlineError';
import { operatingModeOptions } from '@/utils/operatingMode';
import type { PolicyMode } from './types';

type PolicyModeSelectorProps = {
	value: PolicyMode;
	onChange: (_MODE: PolicyMode) => void;
	error?: Error | null;
	pending?: boolean;
};

export function PolicyModeSkeleton() {
	return (
		<section
			className="mt-10 border-t border-stone-300 pt-6"
			aria-label="Loading policy mode"
			aria-busy="true"
		>
			<div className="flex min-w-0 flex-col gap-4 sm:flex-row sm:items-center">
				<h2 className="flex items-center gap-3 text-base font-medium text-primary">
					<LuShieldCheck size={24} aria-hidden="true" />
					Mode
				</h2>
				<div className="h-11 w-full animate-pulse rounded-control bg-stone-200 sm:max-w-md" />
			</div>
		</section>
	);
}

export default function PolicyModeSelector({
	value,
	onChange,
	error,
	pending = false,
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
					options={operatingModeOptions}
					selectedValue={value}
					onChange={onChange}
					disabled={pending}
					className="min-w-0 flex-1 sm:max-w-md"
				/>
			</div>
			{error && <InlineError className="mt-3">{error.message}</InlineError>}
		</section>
	);
}
