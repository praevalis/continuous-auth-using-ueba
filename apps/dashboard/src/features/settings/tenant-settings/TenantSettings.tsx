import { useCallback, useEffect, useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import ConfigurationStatus from './ConfigurationStatus';
import CurrentConfiguration from './CurrentConfiguration';
import { api } from '@/api/client';
import { useTenant } from '@/api/tenant';
import type { TenantSettingsData } from './types';
import TenantIdentity from './TenantIdentity';
import TenantSettingsIntro from './TenantSettingsIntro';

export default function TenantSettings() {
	const { tenant: selectedTenant } = useTenant();
	const [data, setData] = useState<TenantSettingsData | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [saving, setSaving] = useState(false);
	const [displayName, setDisplayName] = useState('');
	const [timezone, setTimezone] = useState('UTC');
	const load = useCallback(async () => {
		if (!selectedTenant) return;
		setData(null);
		setError(null);
		try {
			const [modes, profiles] = await Promise.all([
				api.listModes(selectedTenant.id),
				api.listProfiles(selectedTenant.id),
			]);
			const operatingMode = modes.find((item) => item.is_active) ?? modes[0];
			const thresholdProfile =
				profiles.find((item) => item.is_active) ?? profiles[0];
			if (!operatingMode || !thresholdProfile) return;
			setDisplayName(selectedTenant.display_name);
			setTimezone(selectedTenant.default_timezone);
			setData({
				tenant: selectedTenant,
				operatingMode,
				thresholdProfile,
				configurationStatus: {
					provider: 'not_connected',
					ingestion: 'not_configured',
					riskSettings: 'configured',
				},
			});
		} catch (reason) {
			setError(
				reason instanceof Error
					? reason.message
					: 'Unable to load tenant settings',
			);
		}
	}, [selectedTenant]);
	useEffect(() => {
		queueMicrotask(() => void load());
	}, [load]);
	if (error)
		return (
			<PageLayout title="Tenant settings">
				<p className="mt-10 text-sm text-lockout">{error}</p>
			</PageLayout>
		);
	if (!data)
		return (
			<PageLayout title="Tenant settings">
				<p className="mt-10 text-sm text-carbon-500">
					Loading tenant settings…
				</p>
			</PageLayout>
		);
	const { tenant, operatingMode, thresholdProfile, configurationStatus } = data;

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
					onSave={() => {
						setSaving(true);
						void api
							.updateTenant(tenant.id, {
								display_name: displayName,
								default_timezone: timezone,
							})
							.then((updated) =>
								setData((current) =>
									current ? { ...current, tenant: updated } : current,
								),
							)
							.finally(() => setSaving(false));
					}}
					isSaveDisabled={
						(displayName === tenant.display_name &&
							timezone === tenant.default_timezone) ||
						saving
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
