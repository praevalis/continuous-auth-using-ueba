import { useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import ConfigurationStatus from './ConfigurationStatus';
import CurrentConfiguration from './CurrentConfiguration';
import { mockTenantSettings } from './mock-data';
import TenantIdentity from './TenantIdentity';
import TenantSettingsIntro from './TenantSettingsIntro';

export default function TenantSettings() {
	const { tenant, operatingMode, thresholdProfile, configurationStatus } =
		mockTenantSettings;
	const [displayName, setDisplayName] = useState(tenant.display_name);
	const [timezone, setTimezone] = useState(tenant.default_timezone);

	return (
		<PageLayout title="Tenant settings">
			<TenantSettingsIntro />
			<div className="mt-8">
				<TenantIdentity
					tenant={tenant}
					displayName={displayName}
					timezone={timezone}
					onDisplayNameChange={setDisplayName}
					onTimezoneChange={setTimezone}
					onSave={() => undefined}
					isSaveDisabled={
						displayName === tenant.display_name &&
						timezone === tenant.default_timezone
					}
				/>
				<CurrentConfiguration
					operatingMode={operatingMode}
					thresholdProfile={thresholdProfile}
				/>
				<ConfigurationStatus
					status={configurationStatus}
					profile={thresholdProfile}
				/>
			</div>
		</PageLayout>
	);
}
