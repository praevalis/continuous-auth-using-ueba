import type { OperatingMode, ThresholdProfile } from '@/api/contracts';
import { operatingModeLabels } from '@/utils/operatingMode';

function formatDate(value: string) {
	return new Intl.DateTimeFormat('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
		timeZone: 'UTC',
	}).format(new Date(value));
}

export default function CurrentConfiguration({
	operatingMode,
	thresholdProfile,
}: {
	operatingMode: OperatingMode;
	thresholdProfile: ThresholdProfile;
}) {
	const rows = [
		['Operating mode', operatingModeLabels[operatingMode.mode]],
		['Effective from', formatDate(operatingMode.effective_from)],
		['Risk settings profile', thresholdProfile.name],
		['Caution threshold', thresholdProfile.caution_threshold.toFixed(3)],
		['Lockout threshold', thresholdProfile.lockout_threshold.toFixed(3)],
		['Active', thresholdProfile.is_active ? 'Yes' : 'No'],
	];

	return (
		<section
			className="grid gap-6 border-t border-stone-300 py-8 lg:grid-cols-[15rem_minmax(0,1fr)]"
			aria-labelledby="current-configuration-heading"
		>
			<div>
				<h2
					id="current-configuration-heading"
					className="text-section-title text-primary"
				>
					Current configuration
				</h2>
				<p className="mt-3 max-w-xs text-sm leading-5 text-carbon-300">
					View the key settings that are currently applied to your tenant.
				</p>
			</div>
			<dl className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-x-6 gap-y-3 text-sm sm:max-w-xl">
				{rows.map(([label, value]) => (
					<div key={label} className="contents">
						<dt className="text-carbon-700">{label}</dt>
						<dd className="text-primary">{value}</dd>
					</div>
				))}
			</dl>
		</section>
	);
}
