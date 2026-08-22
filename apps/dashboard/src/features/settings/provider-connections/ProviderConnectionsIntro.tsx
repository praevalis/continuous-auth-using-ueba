import { LuPlus } from 'react-icons/lu';

export default function ProviderConnectionsIntro({
	onAdd,
}: {
	onAdd: () => void;
}) {
	return (
		<section aria-labelledby="response-providers-heading">
			<div className="flex items-center gap-3 text-label uppercase tracking-[0.12em] text-carbon-300">
				<span className="h-1 w-5 rounded-full bg-caution" aria-hidden="true" />
				<span>Integrations</span>
				<span className="h-1 w-5 rounded-full bg-caution" aria-hidden="true" />
			</div>
			<div className="mt-2 flex flex-col items-start gap-5 lg:flex-row lg:items-start lg:justify-between lg:gap-8">
				<div>
					<h1
						id="response-providers-heading"
						className="max-w-4xl text-3xl font-semibold leading-tight tracking-[-0.035em] text-primary sm:text-4xl"
					>
						Response providers
					</h1>
					<p className="mt-3 max-w-2xl text-base text-carbon-300">
						Configure the services used to deliver automated response actions.
					</p>
				</div>
				<button
					type="button"
					onClick={onAdd}
					className="inline-flex min-h-10 items-center justify-center gap-2 rounded-control border border-stone-300 px-4 py-2 text-sm text-primary transition hover:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary lg:mt-1"
				>
					<LuPlus size={17} />
					Add response provider
				</button>
			</div>
		</section>
	);
}
