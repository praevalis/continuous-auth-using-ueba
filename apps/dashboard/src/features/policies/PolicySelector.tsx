import Badge from '@/components/ui/Badge';
import Dropdown from '@/components/ui/Dropdown';
import type { Policy } from './types';

type PolicySelectorProps = {
	policies: Policy[];
	selectedPolicy: Policy;
	onSelect: (_ID: string) => void;
};

export function PolicySelectorSkeleton() {
	return (
		<div
			className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center"
			aria-hidden="true"
		>
			<span className="text-base font-semibold text-primary">Policy</span>
			<div className="h-11 w-full min-w-0 rounded-control border border-stone-300 sm:w-[24rem] sm:flex-none">
				<div className="h-full w-32 animate-pulse rounded-control bg-stone-200" />
			</div>
			<span className="h-6 w-16 animate-pulse rounded-control bg-stone-200" />
		</div>
	);
}

export function PolicySelectorEmpty({ onRetry }: { onRetry?: () => void }) {
	return (
		<div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
			<label
				className="text-base font-semibold text-primary"
				htmlFor="policy-select"
			>
				Policy
			</label>
			<div className="h-11 w-full min-w-0 rounded-control border border-stone-300 bg-transparent text-sm sm:w-[24rem] sm:flex-none">
				<Dropdown
					id="policy-select"
					label="No profiles available"
					options={[]}
					fullWidth
					disabled
				/>
			</div>
			{onRetry && (
				<button
					type="button"
					className="rounded-control border border-primary px-4 py-2 text-sm text-primary"
					onClick={onRetry}
				>
					Retry
				</button>
			)}
		</div>
	);
}

export default function PolicySelector({
	policies,
	selectedPolicy,
	onSelect,
}: PolicySelectorProps) {
	return (
		<div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
			<label
				className="text-base font-semibold text-primary"
				htmlFor="policy-select"
			>
				Policy
			</label>
			<div className="h-11 w-full min-w-0 rounded-control border border-stone-300 bg-transparent text-sm sm:w-[24rem] sm:flex-none">
				<Dropdown
					id="policy-select"
					label="Policy"
					options={policies.map((policy) => ({
						label: policy.name,
						value: policy.id,
					}))}
					value={selectedPolicy.id}
					onChange={onSelect}
					fullWidth
				/>
			</div>
			<Badge
				leading={
					<span className="size-2 rounded-full bg-safe" aria-hidden="true" />
				}
				className="min-h-0 self-start px-0 text-sm text-carbon-700 sm:min-h-10 sm:self-auto sm:rounded-control sm:border sm:border-safe/20 sm:bg-safe-soft sm:px-3"
			>
				{selectedPolicy.status === 'active' ? 'Active' : 'Inactive'}
			</Badge>
		</div>
	);
}
