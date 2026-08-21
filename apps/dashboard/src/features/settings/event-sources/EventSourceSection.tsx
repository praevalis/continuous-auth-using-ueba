import { LuBan, LuPencil, LuPlus } from 'react-icons/lu';
import CredentialEntry from './CredentialEntry';
import ResourceStatusBadge from './ResourceStatusBadge';
import type { EventSourceWithCredentials } from './types';

const sourceTypeLabels = {
	idp: 'Identity provider',
	siem: 'SIEM',
	agent: 'Agent',
	manual_replay: 'Manual replay',
} as const;

function formatMetadata(source: EventSourceWithCredentials) {
	return [
		sourceTypeLabels[source.source_type],
		source.vendor,
		source.payload_format?.toUpperCase(),
	]
		.filter(Boolean)
		.join(' · ');
}

export default function EventSourceSection({
	source,
	onIssueCredential,
	onEdit,
	onToggle,
	onRotate,
	onRevoke,
}: {
	source: EventSourceWithCredentials;
	onIssueCredential: () => void;
	onEdit: () => void;
	onToggle: () => void;
	onRotate: (_id: string) => void;
	onRevoke: (_id: string) => void;
}) {
	const active = source.status === 'active';
	return (
		<section className="border-b border-stone-300 py-8 last:border-b-0 lg:grid lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.7fr)] lg:gap-10">
			<div className="relative pl-5 lg:pl-6">
				<span
					className="absolute left-0 top-0 h-24 w-1 rounded-full bg-safe lg:h-19"
					aria-hidden="true"
				/>
				<div className="flex w-full items-start justify-between gap-4">
					<div>
						<h2 className="text-xl font-semibold tracking-[-0.02em] text-primary">
							{source.source_name}
						</h2>
						<div className="mt-3">
							<ResourceStatusBadge
								label={active ? 'Active' : 'Disabled'}
								tone={active ? 'safe' : 'lockout'}
							/>
						</div>
					</div>
					<div className="flex items-center gap-1 lg:hidden">
						<button
							type="button"
							onClick={onEdit}
							aria-label="Edit event source"
							title="Edit event source"
							className="inline-flex items-center gap-1.5 rounded-control px-2 py-1 text-sm text-primary transition hover:bg-primary-soft hover:text-primary active:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
						>
							<LuPencil size={16} />
						</button>
						<button
							type="button"
							onClick={onToggle}
							aria-label={
								active ? 'Disable event source' : 'Activate event source'
							}
							title={active ? 'Disable event source' : 'Activate event source'}
							className="inline-flex items-center gap-1.5 rounded-control px-2 py-1 text-sm text-primary transition hover:bg-primary-soft hover:text-primary active:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
						>
							<LuBan size={16} />
						</button>
					</div>
				</div>
				<p className="mt-4 text-sm text-carbon-500">{formatMetadata(source)}</p>
				<div className="mt-6 hidden items-center gap-5 lg:flex">
					<button
						type="button"
						onClick={onEdit}
						className="inline-flex items-center gap-1.5 rounded-control px-2 py-1 text-sm text-primary transition hover:bg-primary-soft hover:text-primary active:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					>
						<LuPencil size={16} /> Edit
					</button>
					<button
						type="button"
						onClick={onToggle}
						className="inline-flex items-center gap-1.5 rounded-control px-2 py-1 text-sm text-primary transition hover:bg-primary-soft hover:text-primary active:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					>
						<LuBan size={16} /> {active ? 'Disable' : 'Activate'}
					</button>
				</div>
			</div>
			<div className="mt-8 rounded-panel bg-stone-100 p-5 sm:p-6 lg:mt-0 lg:rounded-none lg:border-l lg:border-stone-300 lg:bg-transparent lg:pl-10 lg:pt-0">
				<div className="flex w-full items-center justify-between gap-4">
					<h3 className="text-lg font-semibold tracking-[-0.015em] text-primary">
						Credentials{' '}
						<span className="text-carbon-500">
							({source.credentials.length})
						</span>
					</h3>
					<button
						type="button"
						onClick={onIssueCredential}
						className="inline-flex min-h-8 shrink-0 items-center gap-1.5 rounded-control border border-stone-300 px-2 text-[0.6875rem] text-primary transition hover:bg-primary-soft sm:min-h-9 sm:px-3 sm:text-xs"
					>
						<LuPlus size={14} /> Issue credential
					</button>
				</div>
				<div className="mt-3 divide-y divide-stone-300/80">
					{source.credentials.map((credential) => (
						<CredentialEntry
							key={credential.id}
							credential={credential}
							onRotate={() => onRotate(credential.id)}
							onRevoke={() => onRevoke(credential.id)}
						/>
					))}
				</div>
			</div>
		</section>
	);
}
