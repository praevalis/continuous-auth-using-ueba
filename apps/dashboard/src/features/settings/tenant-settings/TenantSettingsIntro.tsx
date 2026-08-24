import PageHeader from '@/components/ui/PageHeader';

export default function TenantSettingsIntro() {
	return (
		<PageHeader
			eyebrow="Administration"
			title="Manage tenant settings"
			description="View and update your tenant identity, configuration, and risk profile."
			id="tenant-settings-heading"
		/>
	);
}
