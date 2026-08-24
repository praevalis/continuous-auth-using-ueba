import { LuBan, LuPencil, LuPlus } from 'react-icons/lu';
import CredentialEntry from './CredentialEntry';
import ResourceStatusBadge from './ResourceStatusBadge';
import type { EventSourceWithCredentials } from './types';
import Button from '@/components/ui/Button';
import IconButton from '@/components/ui/IconButton';

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
					className={`absolute left-0 top-0 h-24 w-1 rounded-full ${active ? 'bg-safe' : 'bg-lockout'} lg:h-19`}
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
						<IconButton
							icon={<LuPencil size={16} aria-hidden="true" />}
							label="Edit event source"
							onClick={onEdit}
							variant="quiet"
							size="sm"
							className="size-8 p-1 text-primary"
						/>
						<IconButton
							icon={<LuBan size={16} aria-hidden="true" />}
							label={active ? 'Disable event source' : 'Activate event source'}
							onClick={onToggle}
							variant="quiet"
							size="sm"
							className="size-8 p-1 text-primary"
						/>
					</div>
				</div>
				<p className="mt-4 text-sm text-carbon-500">{formatMetadata(source)}</p>
				<div className="mt-6 hidden items-center gap-5 lg:flex">
					<Button
						onClick={onEdit}
						variant="quiet"
						size="sm"
						leading={<LuPencil size={16} aria-hidden="true" />}
						className="min-h-0 px-2 py-1 text-sm"
					>
						Edit
					</Button>
					<Button
						onClick={onToggle}
						variant="quiet"
						size="sm"
						leading={<LuBan size={16} aria-hidden="true" />}
						className="min-h-0 px-2 py-1 text-sm"
					>
						{active ? 'Disable' : 'Activate'}
					</Button>
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
					<Button
						onClick={onIssueCredential}
						disabled={!active}
						title={
							active
								? 'Issue credential'
								: 'Activate the event source to issue a credential'
						}
						leading={<LuPlus size={14} aria-hidden="true" />}
						size="sm"
						className="min-h-8 shrink-0 border-stone-300 px-2 text-[0.6875rem] sm:min-h-9 sm:px-3 sm:text-xs"
					>
						Issue credential
					</Button>
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

export function EventSourceSectionSkeleton() {
	return (
		<section className="border-b border-stone-300 py-8 last:border-b-0 lg:grid lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.7fr)] lg:gap-10">
			<div className="relative pl-5 lg:pl-6">
				<span
					className="absolute left-0 top-0 h-24 w-1 animate-pulse rounded-full bg-stone-200 lg:h-19"
					aria-hidden="true"
				/>
				<div className="h-7 w-48 animate-pulse rounded bg-stone-200" />
				<div className="mt-4 h-6 w-20 animate-pulse rounded bg-stone-200" />
				<div className="mt-5 h-4 w-56 max-w-full animate-pulse rounded bg-stone-200" />
			</div>
			<div className="mt-8 rounded-panel bg-stone-100 p-5 sm:p-6 lg:mt-0 lg:rounded-none lg:border-l lg:border-stone-300 lg:bg-transparent lg:pl-10 lg:pt-0">
				<div className="flex items-center justify-between gap-4">
					<div className="h-6 w-32 animate-pulse rounded bg-stone-200" />
					<div className="h-9 w-28 animate-pulse rounded bg-stone-200" />
				</div>
				<div className="mt-5 h-16 animate-pulse rounded bg-stone-200" />
			</div>
		</section>
	);
}
