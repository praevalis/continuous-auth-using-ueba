import Dropdown from '@/components/ui/Dropdown';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import InlineError from '@/components/ui/InlineError';
import StatusBadge from '@/components/ui/StatusBadge';
import { listTimeZones } from 'timezone-support';
import type { components } from '@/api/generated/types';

const timezoneOptions = listTimeZones()
	.sort((left, right) => left.localeCompare(right))
	.map((timezone) => ({ label: timezone, value: timezone }));

function formatDate(value: string) {
	return new Intl.DateTimeFormat('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
		timeZone: 'UTC',
	}).format(new Date(value));
}

export default function TenantIdentity({
	tenant,
	displayName,
	timezone,
	onDisplayNameChange,
	onTimezoneChange,
	onSave,
	isSaveDisabled,
	saveError,
	isSaving = false,
}: {
	tenant: components['schemas']['TenantSchema'];
	displayName: string;
	timezone: string;
	onDisplayNameChange: (_value: string) => void;
	onTimezoneChange: (_value: string) => void;
	onSave: () => void;
	isSaveDisabled: boolean;
	saveError?: Error | null;
	isSaving?: boolean;
}) {
	return (
		<section
			className="grid gap-6 border-t border-stone-300 py-8 lg:grid-cols-[15rem_minmax(0,1fr)]"
			aria-labelledby="tenant-identity-heading"
		>
			<div>
				<h2
					id="tenant-identity-heading"
					className="text-section-title text-primary"
				>
					Identity
				</h2>
				<p className="mt-3 max-w-xs text-sm leading-5 text-carbon-300">
					View and update your tenant identity information.
				</p>
			</div>
			<div className="max-w-xl">
				<div className="grid gap-4 lg:grid-cols-[11rem_minmax(0,1fr)] lg:items-center">
					<label htmlFor="tenant-display-name" className="text-sm text-primary">
						Display name
					</label>
					<Input
						id="tenant-display-name"
						value={displayName}
						onChange={(event) => onDisplayNameChange(event.target.value)}
						className="h-10 text-primary focus-visible:border-primary"
					/>
					<label htmlFor="tenant-timezone" className="text-sm text-primary">
						Default timezone
					</label>
					<div className="h-10 w-full rounded-control border border-stone-300">
						<Dropdown
							id="tenant-timezone"
							label="Default timezone"
							options={timezoneOptions}
							value={timezone}
							onChange={onTimezoneChange}
							fullWidth
							buttonClassName="text-sm text-primary"
							scrollable
						/>
					</div>
					<div className="grid grid-cols-2 gap-4 lg:col-span-2 lg:contents">
						<span className="text-sm text-primary">Status</span>
						<StatusBadge
							tone={tenant.status === 'active' ? 'safe' : 'neutral'}
							className="text-sm"
						>
							{tenant.status === 'active' ? 'Active' : tenant.status}
						</StatusBadge>
					</div>
					<div className="grid grid-cols-2 gap-4 lg:col-span-2 lg:contents">
						<span className="text-sm text-primary">Created</span>
						<span className="text-sm text-primary">
							{formatDate(tenant.created_at)}
						</span>
					</div>
					<div className="grid grid-cols-2 gap-4 lg:col-span-2 lg:contents">
						<span className="text-sm text-primary">Last updated</span>
						<span className="text-sm text-primary">
							{formatDate(tenant.updated_at)}
						</span>
					</div>
				</div>
				<div className="mt-6 flex justify-end">
					{saveError && (
						<InlineError className="mr-4 self-center">
							{saveError.message}
						</InlineError>
					)}
					<Button
						onClick={onSave}
						disabled={isSaveDisabled}
						loading={isSaving}
						className="border-primary"
					>
						Save changes
					</Button>
				</div>
			</div>
		</section>
	);
}
