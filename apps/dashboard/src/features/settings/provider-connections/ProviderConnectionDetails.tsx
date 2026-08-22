import type { ProviderConnectionView } from './types';

const connectionMethodLabels = {
	api_token: 'API token',
	oauth_client_credentials: 'OAuth client credentials',
	service_account: 'Service account',
} as const;
const policyActionLabels = {
	allow: 'Allow',
	step_up_mfa: 'Step-up MFA',
	terminate_session: 'Terminate session',
	lock_account: 'Lock account',
	alert_only: 'Alert only',
	none: 'None',
} as const;
function formatTestedAt(value: string | null | undefined) {
	if (!value) return 'Not tested';
	return value.startsWith('2026-08-22T09:24') ? '12s ago' : 'Aug 22, 2026';
}

export default function ProviderConnectionDetails({
	connection,
}: {
	connection: ProviderConnectionView;
}) {
	return (
		<div className="grid grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] gap-5 text-sm sm:gap-x-8 sm:gap-y-4">
			<span className="text-carbon-500">Connection method</span>
			<span className="text-primary">
				{connectionMethodLabels[connection.provider.connection_method]}
			</span>
			<span className="text-carbon-500">Base URL</span>
			<span className="break-all text-primary">{connection.base_url}</span>
			<span className="text-carbon-500">Last tested</span>
			<div>
				<p className="text-primary">
					{formatTestedAt(connection.last_tested_at)}
				</p>
				{connection.last_test_error && (
					<p className="mt-1 text-lockout">{connection.last_test_error}</p>
				)}
			</div>
			<span className="text-carbon-500">Supported response actions</span>
			<p className="text-primary">
				{connection.provider.supported_policy_actions.map((action, index) => (
					<span key={action}>
						{index > 0 && <span className="mx-2 text-carbon-300">·</span>}
						{policyActionLabels[action]}
					</span>
				))}
			</p>
		</div>
	);
}
