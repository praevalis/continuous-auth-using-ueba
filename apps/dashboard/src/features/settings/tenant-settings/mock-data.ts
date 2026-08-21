import type { TenantSettingsData } from './types';

export const mockTenantSettings: TenantSettingsData = {
	tenant: {
		id: 'tenant-demo',
		slug: 'demo-tenant',
		display_name: 'Demo tenant',
		status: 'active',
		default_timezone: 'Asia/Kolkata',
		created_at: '2026-08-20T09:24:00Z',
		updated_at: '2026-08-20T09:24:00Z',
	},
	operatingMode: {
		id: 'operating-mode-demo',
		tenant_id: 'tenant-demo',
		mode: 'enforce',
		is_active: true,
		effective_from: '2026-08-20T09:24:00Z',
		effective_to: null,
		changed_by: null,
		change_reason: null,
		created_at: '2026-08-20T09:24:00Z',
	},
	thresholdProfile: {
		id: 'threshold-profile-demo',
		tenant_id: 'tenant-demo',
		name: 'Default risk profile',
		description: 'Default Safe, Caution, and Lockout thresholds.',
		caution_threshold: 0.349,
		lockout_threshold: 0.463,
		fusion_alpha: null,
		is_active: true,
		effective_from: '2026-08-20T09:24:00Z',
		effective_to: null,
		created_at: '2026-08-20T09:24:00Z',
		updated_at: '2026-08-20T09:24:00Z',
	},
	configurationStatus: {
		provider: 'not_connected',
		ingestion: 'not_configured',
		riskSettings: 'configured',
	},
};
