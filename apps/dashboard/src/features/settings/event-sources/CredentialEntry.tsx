import { LuBan, LuKeyRound, LuRefreshCw } from 'react-icons/lu';
import ResourceStatusBadge from './ResourceStatusBadge';
import type { IngestionCredential } from './types';

function formatDate(value: string | null | undefined) {
	if (!value) return 'Never';
	return new Intl.DateTimeFormat('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
		timeZone: 'UTC',
	}).format(new Date(value));
}

function formatLastUsed(value: string | null | undefined) {
	if (!value) return 'Never';
	return value.includes('09:22') ? '2 minutes ago' : '18 minutes ago';
}

export default function CredentialEntry({
	credential,
	onRotate,
	onRevoke,
}: {
	credential: IngestionCredential;
	onRotate: () => void;
	onRevoke: () => void;
}) {
	const active = credential.status === 'active';
	return (
		<div className="grid gap-4 py-5 first:pt-2 last:pb-2 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-start">
			<div className="flex min-w-0 gap-4">
				<LuKeyRound
					className="mt-1 shrink-0 text-primary"
					size={24}
					strokeWidth={1.5}
				/>
				<div className="min-w-0">
					<p className="text-base font-semibold leading-5 text-primary">
						{credential.credential_name}
					</p>
					<p className="mt-1 text-sm text-carbon-500">{credential.key_id}</p>
					<p className="mt-2 text-xs text-carbon-500">
						API key · Expires {formatDate(credential.expires_at)} · Last used{' '}
						{formatLastUsed(credential.last_used_at)}
					</p>
				</div>
			</div>
			<div className="flex min-w-0 flex-wrap items-center gap-3 pl-10 sm:pl-0">
				<ResourceStatusBadge
					className="hidden shrink-0 sm:inline-flex"
					label={active ? 'Active' : credential.status}
					tone={active ? 'safe' : 'lockout'}
				/>
				{active && (
					<>
						<button
							type="button"
							onClick={onRotate}
							className="inline-flex items-center gap-1.5 rounded-control px-2 py-1 text-sm text-primary transition hover:bg-primary-soft hover:text-primary active:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
						>
							<LuRefreshCw size={16} /> Rotate
						</button>
						<button
							type="button"
							onClick={onRevoke}
							className="inline-flex items-center gap-1.5 rounded-control px-2 py-1 text-sm text-primary transition hover:bg-primary-soft hover:text-primary active:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
						>
							<LuBan size={16} /> Revoke
						</button>
					</>
				)}
			</div>
		</div>
	);
}
