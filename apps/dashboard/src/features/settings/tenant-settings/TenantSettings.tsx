import { useCallback, useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import ConfigurationStatus from './ConfigurationStatus';
import CurrentConfiguration from './CurrentConfiguration';
import { useTenant } from '@/hooks/useTenant';
import { useTenantSettings } from '@/hooks/useTenantSettings';
import { useTenantUpdate } from '@/hooks/useTenantUpdate';
import TenantIdentity from './TenantIdentity';
import TenantSettingsIntro from './TenantSettingsIntro';
import ResourceError from '@/components/ui/ResourceError';

export default function TenantSettings() {
	const {
		tenant: selectedTenant,
		loading: tenantLoading,
		error: tenantError,
		refresh: refreshTenant,
	} = useTenant();
	const settings = useTenantSettings(selectedTenant);
	const updateTenant = useTenantUpdate(selectedTenant?.id);
	const tenant = settings.data?.tenant ?? selectedTenant;
	const [draft, setDraft] = useState<{
		tenantId: string;
		displayName: string;
		timezone: string;
	} | null>(null);
	const tenantId = tenant?.id ?? '';
	const displayName =
		draft?.tenantId === tenantId
			? draft.displayName
			: (tenant?.display_name ?? '');
	const timezone =
		draft?.tenantId === tenantId
			? draft.timezone
			: (tenant?.default_timezone ?? 'UTC');
	const updateDraft = useCallback(
		(field: 'displayName' | 'timezone', value: string) => {
			setDraft((current) => {
				const base =
					current?.tenantId === tenantId
						? current
						: {
								tenantId,
								displayName: tenant?.display_name ?? '',
								timezone: tenant?.default_timezone ?? 'UTC',
							};
				return { ...base, [field]: value };
			});
		},
		[tenant, tenantId],
	);

	const handleSave = useCallback(async () => {
		try {
			await updateTenant.mutateAsync({
				display_name: displayName,
				default_timezone: timezone,
			});
			await Promise.all([settings.refresh(), refreshTenant()]);
		} catch {
			// The mutation hook exposes the error for inline presentation.
		}
	}, [displayName, refreshTenant, settings, timezone, updateTenant]);

	const error = tenantError ?? settings.error?.message;
	const loading =
		!error &&
		(tenantLoading || settings.loading || (!!selectedTenant && !settings.data));
	const isSaveDisabled =
		!tenant ||
		loading ||
		updateTenant.pending ||
		(displayName === tenant.display_name &&
			timezone === tenant.default_timezone);

	return (
		<PageLayout title="Tenant settings">
			<TenantSettingsIntro />
			{error && (
				<ResourceError
					className="mt-8"
					title="Unable to load tenant settings"
					error={error}
					onRetry={() =>
						void (tenantError ? refreshTenant() : settings.refresh())
					}
				/>
			)}
			{loading && (
				<div
					className="mt-8 space-y-8"
					aria-label="Loading tenant settings"
					aria-busy="true"
				>
					{Array.from({ length: 3 }, (_, index) => (
						<div
							className="grid gap-6 border-t border-stone-300 py-8 lg:grid-cols-[15rem_minmax(0,1fr)]"
							key={index}
						>
							<div className="space-y-3">
								<span className="block h-5 w-32 animate-pulse rounded bg-stone-200" />
								<span className="block h-3 w-48 animate-pulse rounded bg-stone-200" />
							</div>
							<div className="space-y-3">
								<span className="block h-4 w-64 animate-pulse rounded bg-stone-200" />
								<span className="block h-4 w-48 animate-pulse rounded bg-stone-200" />
								<span className="block h-4 w-56 animate-pulse rounded bg-stone-200" />
							</div>
						</div>
					))}
				</div>
			)}
			{!loading && !error && !settings.data && (
				<p className="mt-10 text-sm text-carbon-500">
					No tenant configuration is available yet.
				</p>
			)}
			{tenant && !loading && (
				<div className="mt-8">
					<TenantIdentity
						tenant={tenant}
						displayName={displayName}
						timezone={timezone}
						onDisplayNameChange={(value) => updateDraft('displayName', value)}
						onTimezoneChange={(value) => updateDraft('timezone', value)}
						onSave={() => void handleSave()}
						isSaveDisabled={isSaveDisabled}
						saveError={updateTenant.error}
						isSaving={updateTenant.pending}
					/>
					{settings.data && (
						<>
							<CurrentConfiguration
								operatingMode={settings.data.operatingMode}
								thresholdProfile={settings.data.thresholdProfile}
							/>
							<ConfigurationStatus
								status={settings.data.configurationStatus}
								profile={settings.data.thresholdProfile}
							/>
						</>
					)}
				</div>
			)}
		</PageLayout>
	);
}
