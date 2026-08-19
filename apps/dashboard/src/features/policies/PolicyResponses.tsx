import { LuPencil } from 'react-icons/lu';
import type { PolicyResponse } from './types';

const toneClasses = {
	safe: { line: 'bg-safe', text: 'text-safe' },
	caution: { line: 'bg-caution', text: 'text-caution' },
	lockout: { line: 'bg-lockout', text: 'text-lockout' },
} as const;

type PolicyResponsesProps = {
	responses: PolicyResponse[];
	onEdit: (_BAND: PolicyResponse['band']) => void;
};

export default function PolicyResponses({
	responses,
	onEdit,
}: PolicyResponsesProps) {
	return (
		<section className="mt-12" aria-label="Policy response rules">
			<div className="grid lg:grid-cols-3 lg:divide-x lg:divide-stone-300">
				{responses.map((response) => {
					const tone = toneClasses[response.band];
					return (
						<article
							key={response.band}
							className="flex min-h-56 flex-col py-6 first:pt-0 last:pb-0 lg:px-6 lg:py-0 lg:first:pl-0 lg:last:pr-0"
						>
							<div className={`h-0.5 w-full ${tone.line}`} aria-hidden="true" />
							<div className="flex flex-1 flex-col pt-5">
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
								<button
									type="button"
									className="mt-auto inline-flex min-h-10 items-center gap-2 pt-4 text-sm text-primary transition hover:text-carbon-300"
									onClick={() => onEdit(response.band)}
								>
									<LuPencil size={16} aria-hidden="true" />
									Edit
								</button>
							</div>
						</article>
					);
				})}
			</div>
		</section>
	);
}
