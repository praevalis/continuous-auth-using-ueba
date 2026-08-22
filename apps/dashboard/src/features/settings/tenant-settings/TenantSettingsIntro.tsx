export default function TenantSettingsIntro() {
	return (
		<section aria-labelledby="tenant-settings-heading">
			<div className="flex items-center gap-3 text-label uppercase tracking-[0.12em] text-carbon-300">
				<span className="h-1 w-5 rounded-full bg-info" aria-hidden="true" />
				<span>Administration</span>
				<span className="h-1 w-5 rounded-full bg-info" aria-hidden="true" />
			</div>
			<h1
				id="tenant-settings-heading"
				className="mt-2 max-w-4xl text-3xl font-semibold leading-tight tracking-[-0.035em] text-primary sm:text-4xl"
			>
				Manage tenant settings
			</h1>
			<p className="mt-3 max-w-2xl text-base text-carbon-300">
				View and update your tenant identity, configuration, and risk profile.
			</p>
		</section>
	);
}
