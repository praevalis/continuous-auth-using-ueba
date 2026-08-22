import { LuClock3 } from 'react-icons/lu';

export default function ActivityIntro() {
	return (
		<section
			className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between"
			aria-labelledby="activity-heading"
		>
			<div>
				<div className="flex items-center gap-3 text-label uppercase tracking-[0.12em] text-carbon-300">
					<span
						className="h-1 w-5 rounded-full bg-lockout"
						aria-hidden="true"
					/>
					<span>Audit</span>
					<span
						className="h-1 w-5 rounded-full bg-lockout"
						aria-hidden="true"
					/>
				</div>
				<h1
					id="activity-heading"
					className="mt-2 max-w-4xl text-3xl font-semibold leading-tight tracking-[-0.035em] text-primary sm:text-4xl"
				>
					Trace what the platform recorded and carried out
				</h1>
				<p className="mt-3 max-w-2xl text-base text-carbon-300">
					Follow analysis, decisions, alerts, and response actions across the
					tenant.
				</p>
			</div>
			<p className="inline-flex min-h-10 items-center gap-2 self-start rounded-md border border-stone-300 px-4 py-2 text-sm text-carbon-300 lg:mt-7">
				<LuClock3 size={16} aria-hidden="true" /> Updated 12s ago
			</p>
		</section>
	);
}
