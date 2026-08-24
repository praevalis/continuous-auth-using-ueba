import { useState } from 'react';
import type { FormEvent } from 'react';
import type { ThresholdProfileCreate } from '@/api/contracts';
import DateTimePicker from '@/components/ui/DateTimePicker';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import InlineError from '@/components/ui/InlineError';
import Slider from '@/components/ui/Slider';
import Textarea from '@/components/ui/Textarea';
import Field from '@/components/ui/Field';

type CreateThresholdProfileDialogProps = {
	onClose: () => void;
	onCreate: (_profile: ThresholdProfileCreate) => Promise<void>;
	pending: boolean;
	error: Error | null;
};

type FormValues = {
	name: string;
	description: string;
	cautionThreshold: string;
	lockoutThreshold: string;
	fusionAlpha: number;
	effectiveFrom: string;
};

function toLocalDateTimeValue(date: Date) {
	const pad = (value: number) => String(value).padStart(2, '0');
	return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function getInitialValues(): FormValues {
	const effectiveFrom = new Date();
	effectiveFrom.setSeconds(0, 0);
	return {
		name: '',
		description: '',
		cautionThreshold: '0.349',
		lockoutThreshold: '0.463',
		fusionAlpha: 0.5,
		effectiveFrom: toLocalDateTimeValue(effectiveFrom),
	};
}

export default function CreateThresholdProfileDialog({
	onClose,
	onCreate,
	pending,
	error,
}: CreateThresholdProfileDialogProps) {
	const [values, setValues] = useState(getInitialValues);
	const [validationError, setValidationError] = useState<string | null>(null);

	function updateValue<Key extends keyof FormValues>(
		key: Key,
		value: FormValues[Key],
	) {
		setValues((current) => ({ ...current, [key]: value }));
	}

	async function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		const cautionThreshold = Number(values.cautionThreshold);
		const lockoutThreshold = Number(values.lockoutThreshold);
		const effectiveFrom = new Date(values.effectiveFrom);

		if (!values.name.trim()) {
			setValidationError('Enter a profile name.');
			return;
		}
		if (
			!Number.isFinite(cautionThreshold) ||
			!Number.isFinite(lockoutThreshold) ||
			cautionThreshold < 0 ||
			lockoutThreshold < 0 ||
			cautionThreshold >= lockoutThreshold
		) {
			setValidationError(
				'Caution must be non-negative and lower than the lockout threshold.',
			);
			return;
		}
		if (Number.isNaN(effectiveFrom.getTime())) {
			setValidationError('Enter a valid effective date.');
			return;
		}

		setValidationError(null);
		try {
			await onCreate({
				name: values.name.trim(),
				description: values.description.trim() || null,
				caution_threshold: cautionThreshold,
				lockout_threshold: lockoutThreshold,
				fusion_alpha: values.fusionAlpha,
				effective_from: effectiveFrom.toISOString(),
			});
		} catch {
			// The mutation error is rendered below while the dialog remains open.
		}
	}

	return (
		<Modal
			eyebrow="Policies"
			title="Create threshold profile"
			titleId="create-threshold-profile-title"
			onClose={onClose}
			closeDisabled={pending}
		>
			<form className="grid gap-3" onSubmit={handleSubmit}>
				<div className="grid grid-cols-2 gap-3">
					<Field label="Profile name" required>
						<Input
							required
							value={values.name}
							onChange={(event) => updateValue('name', event.target.value)}
						/>
					</Field>
					<DateTimePicker
						label="Effective from"
						value={values.effectiveFrom}
						onChange={(value) => updateValue('effectiveFrom', value)}
						align="start"
					/>
				</div>
				<Field
					label={
						<>
							Description <span className="text-carbon-500">(optional)</span>
						</>
					}
				>
					<Textarea
						value={values.description}
						onChange={(event) => updateValue('description', event.target.value)}
						rows={2}
					/>
				</Field>

				<div className="grid gap-1.5 text-sm text-primary">
					<div className="flex items-center justify-between gap-3">
						<label htmlFor="fusion-alpha" className="text-sm text-primary">
							Fusion alpha
						</label>
						<output
							htmlFor="fusion-alpha"
							className="font-mono text-xs text-carbon-700"
						>
							{values.fusionAlpha.toFixed(2)}
						</output>
					</div>
					<Slider
						id="fusion-alpha"
						ariaLabel="Fusion alpha"
						value={values.fusionAlpha}
						onChange={(value) => updateValue('fusionAlpha', value)}
						step={0.01}
						variant="soft-carbon"
					/>
				</div>

				<div className="grid gap-3 sm:grid-cols-2">
					<Field label="Caution threshold" required>
						<Input
							required
							type="number"
							min="0"
							step="0.001"
							value={values.cautionThreshold}
							onChange={(event) =>
								updateValue('cautionThreshold', event.target.value)
							}
						/>
					</Field>
					<Field label="Lockout threshold" required>
						<Input
							required
							type="number"
							min="0"
							step="0.001"
							value={values.lockoutThreshold}
							onChange={(event) =>
								updateValue('lockoutThreshold', event.target.value)
							}
						/>
					</Field>
				</div>

				{(validationError || error) && (
					<InlineError>{validationError ?? error?.message}</InlineError>
				)}
				<div className="mt-1 flex justify-end">
					<Button type="submit" loading={pending} className="border-primary">
						Create
					</Button>
				</div>
			</form>
		</Modal>
	);
}
