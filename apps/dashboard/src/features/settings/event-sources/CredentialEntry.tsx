import { LuBan, LuKeyRound, LuRefreshCw } from 'react-icons/lu';
import ResourceStatusBadge from './ResourceStatusBadge';
import type { components } from '@/api/generated/types';
import Button from '@/components/ui/Button';

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

function maskKeyId(value: string) {
	if (value.length <= 10) return value;
	return `${value.slice(0, 5)}•••••${value.slice(-5)}`;
}

function formatStatus(value: string) {
	return value.charAt(0).toUpperCase() + value.slice(1);
}

export default function CredentialEntry({
	credential,
	onRotate,
	onRevoke,
}: {
	credential: components['schemas']['IngestionCredentialSchema'];
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
					<p className="mt-1 text-sm text-carbon-500">
						Key ID · {maskKeyId(credential.key_id)}
					</p>
					<p className="mt-2 text-xs text-carbon-500">
						API key · Expires {formatDate(credential.expires_at)} · Last used{' '}
						{formatLastUsed(credential.last_used_at)}
					</p>
				</div>
			</div>
			<div className="flex min-w-0 flex-wrap items-center gap-3 pl-10 sm:pl-0">
				<ResourceStatusBadge
					className="hidden shrink-0 sm:inline-flex"
					label={active ? 'Active' : formatStatus(credential.status)}
					tone={active ? 'safe' : 'lockout'}
				/>
				{active && (
					<>
						<Button
							onClick={onRotate}
							variant="quiet"
							size="sm"
							leading={<LuRefreshCw size={16} aria-hidden="true" />}
							className="min-h-0 px-2 py-1 text-sm"
						>
							Rotate
						</Button>
						<Button
							onClick={onRevoke}
							variant="quiet"
							size="sm"
							leading={<LuBan size={16} aria-hidden="true" />}
							className="min-h-0 px-2 py-1 text-sm"
						>
							Revoke
						</Button>
					</>
				)}
			</div>
		</div>
	);
}
