import type { OperatingMode, Tenant, ThresholdProfile } from '@/api/contracts';

export type ConfigurationState =
	'configured' | 'not_configured' | 'not_connected';

export type TenantConfigurationStatus = {
	provider: ConfigurationState;
	ingestion: ConfigurationState;
	riskSettings: ConfigurationState;
};

export type TenantSettingsData = {
	tenant: Tenant;
	operatingMode: OperatingMode;
	thresholdProfile: ThresholdProfile;
	configurationStatus: TenantConfigurationStatus;
};
