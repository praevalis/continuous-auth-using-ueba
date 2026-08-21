import type { components } from '@/api/generated/types';

export type Tenant = components['schemas']['TenantSchema'];
export type OperatingMode = components['schemas']['TenantOperatingModeSchema'];
export type ThresholdProfile =
	components['schemas']['TenantThresholdProfileSchema'];

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
