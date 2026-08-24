import { useState } from 'react';
import type { FormEvent } from 'react';
import type { EventSource } from '@/api/contracts';
import Dropdown from '@/components/ui/Dropdown';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';

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

export type EventSourceFormValues = {
	source_name: string;
	source_type: EventSource['source_type'];
	payload_format: NonNullable<EventSource['payload_format']>;
	vendor: string;
	external_reference: string;
};

function getInitialValues(source?: EventSource): EventSourceFormValues {
	return {
		source_name: source?.source_name ?? '',
		source_type: source?.source_type ?? 'idp',
		payload_format: source?.payload_format ?? 'json',
		vendor: source?.vendor ?? '',
		external_reference: source?.external_reference ?? '',
	};
}

export default function EventSourceDialog({
	source,
	onClose,
	onSubmit,
	pending,
	error,
}: {
	source?: EventSource;
	onClose: () => void;
	onSubmit: (_values: EventSourceFormValues) => Promise<void>;
	pending: boolean;
	error: Error | null;
}) {
	const [values, setValues] = useState(() => getInitialValues(source));
	const [validationError, setValidationError] = useState<string | null>(null);
	const editing = !!source;

	function updateValue<Key extends keyof EventSourceFormValues>(
		key: Key,
		value: EventSourceFormValues[Key],
	) {
		setValues((current) => ({ ...current, [key]: value }));
	}

	async function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		if (!values.source_name.trim()) {
			setValidationError('Enter a source name.');
			return;
		}

		setValidationError(null);
		try {
			await onSubmit({
				...values,
				source_name: values.source_name.trim(),
				vendor: values.vendor.trim(),
				external_reference: values.external_reference.trim(),
			});
		} catch {
			// The mutation error is rendered below while the dialog remains open.
		}
	}

	return (
		<Modal
			eyebrow="Ingestion"
			title={editing ? 'Edit event source' : 'Add event source'}
			titleId="event-source-dialog-title"
			onClose={onClose}
			closeDisabled={pending}
		>
			<form className="grid gap-3" onSubmit={handleSubmit}>
				<label className="grid gap-1.5 text-sm text-primary">
					<span>Source name</span>
					<Input
						required
						value={values.source_name}
						onChange={(event) => updateValue('source_name', event.target.value)}
					/>
				</label>
				<div className="grid gap-3 sm:grid-cols-2">
					<label className="grid gap-1.5 text-sm text-primary">
						<span>Source type</span>
						<div className="h-9 rounded-control border border-stone-300">
							<Dropdown
								label="Source type"
								options={sourceTypeOptions}
								value={values.source_type}
								onChange={(value) =>
									updateValue(
										'source_type',
										value as EventSource['source_type'],
									)
								}
								fullWidth
								buttonClassName="text-sm text-primary"
							/>
						</div>
					</label>
					<label className="grid gap-1.5 text-sm text-primary">
						<span>Payload format</span>
						<div className="h-9 rounded-control border border-stone-300">
							<Dropdown
								label="Payload format"
								options={payloadFormatOptions}
								value={values.payload_format}
								onChange={(value) =>
									updateValue(
										'payload_format',
										value as NonNullable<EventSource['payload_format']>,
									)
								}
								fullWidth
								buttonClassName="text-sm text-primary"
							/>
						</div>
					</label>
				</div>
				<div className="grid gap-3 sm:grid-cols-2">
					<label className="grid gap-1.5 text-sm text-primary">
						<span>
							Vendor <span className="text-carbon-500">(optional)</span>
						</span>
						<Input
							value={values.vendor}
							onChange={(event) => updateValue('vendor', event.target.value)}
						/>
					</label>
					<label className="grid gap-1.5 text-sm text-primary">
						<span>
							External reference{' '}
							<span className="text-carbon-500">(optional)</span>
						</span>
						<Input
							value={values.external_reference}
							onChange={(event) =>
								updateValue('external_reference', event.target.value)
							}
						/>
					</label>
				</div>
				{(validationError || error) && (
					<p className="text-sm text-lockout" role="alert">
						{validationError ?? error?.message}
					</p>
				)}
				<div className="mt-1 flex justify-end">
					<button
						type="submit"
						disabled={pending}
						className="rounded-control border border-primary px-3 py-1.5 text-sm text-primary transition hover:bg-primary-soft disabled:cursor-not-allowed disabled:opacity-50"
					>
						{pending
							? editing
								? 'Saving…'
								: 'Adding…'
							: editing
								? 'Save'
								: 'Add'}
					</button>
				</div>
			</form>
		</Modal>
	);
}
