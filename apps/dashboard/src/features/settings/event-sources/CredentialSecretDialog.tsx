import { useState } from 'react';
import { LuCopy, LuCheck } from 'react-icons/lu';
import Modal from '@/components/ui/Modal';

export default function CredentialSecretDialog({
	secret,
	onClose,
}: {
	secret: string;
	onClose: () => void;
}) {
	const [copied, setCopied] = useState(false);
	const [copyError, setCopyError] = useState(false);

	async function handleCopy() {
		if (!navigator.clipboard) {
			setCopyError(true);
			return;
		}

		try {
			await navigator.clipboard.writeText(secret);
			setCopied(true);
			setCopyError(false);
		} catch {
			setCopyError(true);
		}
	}

	return (
		<Modal
			eyebrow="Credentials"
			title="Copy credential secret"
			titleId="credential-secret-dialog-title"
			onClose={onClose}
		>
			<p className="text-sm text-carbon-500">
				This secret will only be displayed once. Copy it before closing this
				dialog.
			</p>
			<div className="mt-4 rounded-control border border-stone-300 bg-stone-100 p-3">
				<code className="block break-all font-mono text-xs text-carbon-700">
					{secret}
				</code>
			</div>
			<div className="mt-4 flex items-center justify-between gap-3">
				{copyError ? (
					<p className="text-xs text-lockout" role="alert">
						Unable to copy. Select the secret manually.
					</p>
				) : (
					<span aria-live="polite" className="text-xs text-carbon-500">
						{copied ? 'Copied to clipboard.' : 'Keep this secret secure.'}
					</span>
				)}
				<button
					type="button"
					onClick={() => void handleCopy()}
					className="inline-flex shrink-0 items-center gap-1.5 rounded-control border border-primary px-3 py-1.5 text-sm text-primary transition hover:bg-primary-soft"
				>
					{copied ? <LuCheck size={15} /> : <LuCopy size={15} />}
					{copied ? 'Copied' : 'Copy secret'}
				</button>
			</div>
		</Modal>
	);
}
