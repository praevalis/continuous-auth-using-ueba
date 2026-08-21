import { NavLink } from 'react-router-dom';
import Badge from '@/components/ui/Badge';
import ActiveRiskProfile from './ActiveRiskProfile';
import type {
	ConfigurationState,
	TenantConfigurationStatus,
	ThresholdProfile,
} from './types';

const statusContent: Record<
	ConfigurationState,
	{ label: string; className: string }
> = {
	configured: { label: 'Configured', className: 'text-safe' },
	not_connected: { label: 'Not connected', className: 'text-lockout' },
	not_configured: { label: 'Not configured', className: 'text-lockout' },
};

const resources = [
	{
		key: 'provider',
		label: 'Provider',
		path: '/settings/providers',
		action: 'Configure provider',
	},
	{
		key: 'ingestion',
		label: 'Ingestion',
		path: '/settings/event-sources',
		action: 'Configure ingestion',
	},
	{
		key: 'riskSettings',
		label: 'Risk settings',
		path: '/policies',
		action: 'Manage risk settings',
	},
] as const;

function StatusBadge({ state }: { state: ConfigurationState }) {
	const content = statusContent[state];
	const leading = (
		<span
			className={`size-2 rounded-full ${state === 'configured' ? 'bg-safe' : 'bg-lockout'}`}
			aria-hidden="true"
		/>
	);

	return (
		<Badge className={`text-xs ${content.className}`} leading={leading}>
			{content.label}
		</Badge>
	);
}

export default function ConfigurationStatus({
	status,
	profile,
}: {
	status: TenantConfigurationStatus;
	profile: ThresholdProfile;
}) {
	return (
		<section
			className="grid gap-8 border-t border-stone-300 py-8 lg:grid-cols-[15rem_minmax(0,1fr)_minmax(0,1fr)]"
			aria-labelledby="configuration-status-heading"
		>
			<div>
				<h2
					id="configuration-status-heading"
					className="text-section-title text-primary"
				>
					Configuration status
				</h2>
				<p className="mt-3 max-w-xs text-sm leading-5 text-carbon-300">
					Review the deployment and configuration of your tenant.
				</p>
			</div>
			<div className="grid grid-cols-3 text-xs sm:gap-4 sm:text-sm lg:col-span-1">
				{resources.map((resource) => (
					<div
						key={resource.key}
						className="col-span-3 grid grid-cols-3 items-center gap-2 py-3 first:pt-0 last:pb-0 sm:gap-4 lg:border-b lg:border-stone-300 lg:py-3 lg:first:pt-0 lg:last:border-b-0"
					>
						<span className="text-primary">{resource.label}</span>
						<StatusBadge state={status[resource.key]} />
						<NavLink
							to={resource.path}
							className="inline-flex min-h-9 min-w-0 items-center justify-center rounded-control border border-stone-300 px-2 text-center text-[0.6875rem] text-primary transition hover:bg-primary-soft sm:px-3 sm:text-xs"
						>
							{resource.action}
						</NavLink>
					</div>
				))}
			</div>
			<ActiveRiskProfile profile={profile} />
		</section>
	);
}
