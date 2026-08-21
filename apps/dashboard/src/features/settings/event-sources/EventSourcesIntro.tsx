export default function EventSourcesIntro({ onAdd }: { onAdd: () => void }) {
	return (
		<section aria-labelledby="event-sources-heading">
			<p className="text-label uppercase tracking-[0.12em] text-carbon-300">
				Ingestion
			</p>
			<div className="mt-2 flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between lg:gap-8">
				<div>
					<h1
						id="event-sources-heading"
						className="order-1 max-w-4xl text-3xl font-semibold leading-tight tracking-[-0.035em] text-primary sm:text-4xl lg:order-0"
					>
						Manage event sources and credentials
					</h1>
					<p className="mt-3 max-w-2xl text-base text-carbon-300">
						Configure where authentication events come from and manage the
						credentials used to send them.
					</p>
				</div>
				<button
					type="button"
					onClick={onAdd}
					className="inline-flex min-h-10 shrink-0 items-center justify-center self-start rounded-control border border-primary px-4 py-2 text-sm text-primary transition hover:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary lg:mt-1"
				>
					Add event source
				</button>
			</div>
		</section>
	);
}
