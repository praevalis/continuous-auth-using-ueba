type PoliciesIntroProps = {
	onCreatePolicy: () => void;
};

export default function PoliciesIntro({ onCreatePolicy }: PoliciesIntroProps) {
	return (
		<section aria-labelledby="policies-heading">
			<div className="flex items-center gap-3 text-label uppercase tracking-[0.12em] text-carbon-300">
				<span className="h-1 w-5 rounded-full bg-info" aria-hidden="true" />
				<span>Control</span>
				<span className="h-1 w-5 rounded-full bg-info" aria-hidden="true" />
			</div>
			<div className="mt-2 flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
				<div>
					<h1
						id="policies-heading"
						className="max-w-4xl text-3xl font-semibold leading-tight tracking-[-0.035em] text-primary sm:text-4xl"
					>
						Set the rules for sign-in decisions
					</h1>
					<p className="mt-3 max-w-2xl text-base text-carbon-300">
						Create and manage the policies that guide continuous authentication
						responses.
					</p>
				</div>
				<button
					type="button"
					className="hidden min-h-10 shrink-0 rounded-control border border-primary px-4 py-2 text-sm text-primary transition hover:bg-primary-soft lg:inline-flex lg:items-center lg:justify-center"
					onClick={onCreatePolicy}
				>
					Create policy
				</button>
			</div>
		</section>
	);
}
