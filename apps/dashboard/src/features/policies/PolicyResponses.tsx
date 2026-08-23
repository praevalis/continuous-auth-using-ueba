import type { PolicyResponse } from './types';

const toneClasses = {
	safe: { line: 'bg-safe', text: 'text-safe' },
	caution: { line: 'bg-caution', text: 'text-caution' },
	lockout: { line: 'bg-lockout', text: 'text-lockout' },
} as const;

type PolicyResponsesProps = {
	responses: PolicyResponse[];
};

export function PolicyResponsesSkeleton() {
	return (
		<section
			className="mt-12"
			aria-label="Loading policy response rules"
			aria-busy="true"
		>
			<div className="grid lg:grid-cols-3 lg:divide-x lg:divide-stone-300">
				{['safe', 'caution', 'lockout'].map((band) => (
					<article
						key={band}
						className="flex min-h-48 flex-col py-6 first:pt-0 last:pb-0 lg:px-6 lg:py-0 lg:first:pl-0 lg:last:pr-0"
						aria-hidden="true"
					>
						<div className="h-0.5 w-full bg-stone-200" />
						<div className="flex flex-col pt-5">
							<div className="flex items-center gap-3">
								<span className="size-3 animate-pulse rounded-full bg-stone-200" />
								<span className="h-4 w-20 animate-pulse rounded bg-stone-200" />
							</div>
							<span className="mt-5 h-5 w-44 animate-pulse rounded bg-stone-200" />
							<div className="mt-3 max-w-sm space-y-2">
								<span className="block h-3 w-full animate-pulse rounded bg-stone-200" />
								<span className="block h-3 w-3/4 animate-pulse rounded bg-stone-200" />
							</div>
						</div>
					</article>
				))}
			</div>
		</section>
	);
}

export default function PolicyResponses({ responses }: PolicyResponsesProps) {
	return (
		<section className="mt-12" aria-label="Policy response rules">
			<div className="grid lg:grid-cols-3 lg:divide-x lg:divide-stone-300">
				{responses.map((response) => {
					const tone = toneClasses[response.band];
					return (
						<article
							key={response.band}
							className="flex min-h-48 flex-col py-6 first:pt-0 last:pb-0 lg:px-6 lg:py-0 lg:first:pl-0 lg:last:pr-0"
						>
							<div className={`h-0.5 w-full ${tone.line}`} aria-hidden="true" />
							<div className="flex flex-col pt-5">
								<div
									className={`flex items-center gap-3 font-semibold ${tone.text}`}
								>
									<span
										className="size-3 rounded-full bg-current"
										aria-hidden="true"
									/>
									{response.label}
								</div>
								<h3 className="mt-5 text-base font-semibold text-primary">
									{response.action}
								</h3>
								<p className="mt-2 max-w-sm text-sm leading-6 text-carbon-300">
									{response.description}
								</p>
							</div>
						</article>
					);
				})}
			</div>
		</section>
	);
}
