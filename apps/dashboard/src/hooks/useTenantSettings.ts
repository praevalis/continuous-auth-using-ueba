import { useCallback } from 'react';
import { api } from '@/api/client';
import type { Tenant } from '@/api/contracts';
import type { TenantSettingsData } from '@/features/settings/tenant-settings/types';
import { useAsyncResource } from './useAsyncResource';

export function useTenantSettings(tenant: Tenant | null) {
	const load = useCallback(async (): Promise<TenantSettingsData | null> => {
		if (!tenant) return null;
		const [modes, profiles, eventSources, credentials, providerConnections] =
			await Promise.all([
				api.listModes(tenant.id),
				api.listProfiles(tenant.id),
				api.listEventSources(tenant.id),
				api.listCredentials(tenant.id),
				api.listConnections(tenant.id),
			]);
		const operatingMode = modes.find((item) => item.is_active) ?? modes[0];
		const thresholdProfile =
			profiles.find((item) => item.is_active) ?? profiles[0];

		if (!operatingMode || !thresholdProfile) return null;

		const hasConfiguredIngestion = eventSources.some(
			(source) =>
				source.status === 'active' &&
				credentials.some(
					(credential) =>
						credential.status === 'active' &&
						credential.event_source_id === source.id,
				),
		);
		const hasConfiguredProvider = providerConnections.some(
			(connection) => connection.status === 'active',
		);

		return {
			tenant,
			operatingMode,
			thresholdProfile,
			configurationStatus: {
				provider: hasConfiguredProvider ? 'configured' : 'not_connected',
				ingestion: hasConfiguredIngestion ? 'configured' : 'not_configured',
				riskSettings:
					operatingMode.is_active && thresholdProfile.is_active
						? 'configured'
						: 'not_configured',
			},
		};
	}, [tenant]);
	return useAsyncResource(load, !!tenant);
}
