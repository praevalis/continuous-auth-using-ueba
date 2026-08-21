import { useState } from 'react';
import type { FormEvent } from 'react';
import { LuX } from 'react-icons/lu';
import Dropdown from '@/components/ui/Dropdown';
import type { EventSourceWithCredentials } from './types';

const sourceTypeOptions = [
	{ label: 'Identity provider', value: 'idp' },
	{ label: 'SIEM', value: 'siem' },
	{ label: 'Agent', value: 'agent' },
	{ label: 'Manual replay', value: 'manual_replay' },
];

const payloadFormatOptions = [
	{ label: 'JSON', value: 'json' },
	{ label: 'Syslog', value: 'syslog' },
];

export default function AddEventSourceDialog({
	onClose,
	onCreate,
}: {
	onClose: () => void;
	onCreate: (_source: EventSourceWithCredentials) => void;
}) {
	const [sourceName, setSourceName] = useState('');
	const [sourceType, setSourceType] = useState('idp');
	const [payloadFormat, setPayloadFormat] = useState('json');
	const [vendor, setVendor] = useState('');
	const [externalReference, setExternalReference] = useState('');

	function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		if (!sourceName.trim()) return;
		const now = new Date().toISOString();
		onCreate({
			id: `source-${Date.now()}`,
			tenant_id: 'tenant-demo',
			source_name: sourceName.trim(),
			source_type: sourceType as EventSourceWithCredentials['source_type'],
			payload_format:
				payloadFormat as EventSourceWithCredentials['payload_format'],
			vendor: vendor.trim() || null,
			external_reference: externalReference.trim() || null,
			status: 'active',
			created_at: now,
			updated_at: now,
			credentials: [],
		});
		onClose();
	}

	return (
		<div
			className="fixed inset-0 z-50 flex items-start justify-center bg-primary/20 px-4 py-8 sm:items-center"
			role="presentation"
		>
			<div
				className="w-full max-w-xl rounded-panel bg-paper-50 p-6 shadow-floating sm:p-8"
				role="dialog"
				aria-modal="true"
				aria-labelledby="add-event-source-title"
			>
				<div className="flex items-start justify-between gap-4">
					<div>
						<p className="text-label uppercase tracking-[0.12em] text-carbon-300">
							Ingestion
						</p>
						<h2
							id="add-event-source-title"
							className="mt-2 text-xl font-semibold text-primary"
						>
							Add event source
						</h2>
					</div>
					<button
						type="button"
						onClick={onClose}
						aria-label="Close dialog"
						className="rounded-control p-2 text-carbon-500 transition hover:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					>
						<LuX size={18} />
					</button>
				</div>
				<form className="mt-6 grid gap-5" onSubmit={handleSubmit}>
					<label className="grid gap-2 text-sm text-primary">
						<span>Source name</span>
						<input
							required
							value={sourceName}
							onChange={(event) => setSourceName(event.target.value)}
							className="h-10 rounded-control border border-stone-300 bg-transparent px-3 text-sm outline-none focus-visible:border-primary"
						/>
					</label>
					<div className="grid gap-5 sm:grid-cols-2">
						<label className="grid gap-2 text-sm text-primary">
							<span>Source type</span>
							<div className="h-10 rounded-control border border-stone-300">
								<Dropdown
									label="Source type"
									options={sourceTypeOptions}
									value={sourceType}
									onChange={setSourceType}
									fullWidth
									buttonClassName="text-sm text-primary"
								/>
							</div>
						</label>
						<label className="grid gap-2 text-sm text-primary">
							<span>Payload format</span>
							<div className="h-10 rounded-control border border-stone-300">
								<Dropdown
									label="Payload format"
									options={payloadFormatOptions}
									value={payloadFormat}
									onChange={setPayloadFormat}
									fullWidth
									buttonClassName="text-sm text-primary"
								/>
							</div>
						</label>
					</div>
					<div className="grid gap-5 sm:grid-cols-2">
						<label className="grid gap-2 text-sm text-primary">
							<span>
								Vendor <span className="text-carbon-500">(optional)</span>
							</span>
							<input
								value={vendor}
								onChange={(event) => setVendor(event.target.value)}
								className="h-10 rounded-control border border-stone-300 bg-transparent px-3 text-sm outline-none focus-visible:border-primary"
							/>
						</label>
						<label className="grid gap-2 text-sm text-primary">
							<span>
								External reference{' '}
								<span className="text-carbon-500">(optional)</span>
							</span>
							<input
								value={externalReference}
								onChange={(event) => setExternalReference(event.target.value)}
								className="h-10 rounded-control border border-stone-300 bg-transparent px-3 text-sm outline-none focus-visible:border-primary"
							/>
						</label>
					</div>
					<div className="mt-2 flex justify-end gap-3">
						<button
							type="button"
							onClick={onClose}
							className="rounded-control px-4 py-2 text-sm text-primary transition hover:bg-primary-soft"
						>
							Cancel
						</button>
						<button
							type="submit"
							className="rounded-control border border-primary px-4 py-2 text-sm text-primary transition hover:bg-primary-soft"
						>
							Add event source
						</button>
					</div>
				</form>
			</div>
		</div>
	);
}
