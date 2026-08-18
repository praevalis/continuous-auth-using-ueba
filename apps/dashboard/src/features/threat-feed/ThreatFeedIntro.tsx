export default function ThreatFeedIntro() {
	return (
		<section
			className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between"
			aria-labelledby="threat-feed-heading"
		>
			<div>
				<p className="text-label uppercase tracking-[0.12em] text-carbon-300">
					Monitor
				</p>
				<h1
					id="threat-feed-heading"
					className="mt-2 max-w-4xl text-3xl font-semibold leading-tight tracking-[-0.035em] text-primary sm:text-4xl"
				>
					Review sign-in events as they arrive
				</h1>
				<p className="mt-3 max-w-2xl text-base text-carbon-300">
					Find sign-in activity that needs attention and understand the response
					decision.
				</p>
			</div>
			<p className="inline-flex min-h-10 items-center rounded-md border border-stone-300 bg-paper-50 px-4 py-2 text-sm leading-5 text-carbon-700 lg:mt-7 lg:max-w-xs">
				12 decisions need review.
			</p>
		</section>
	);
}
