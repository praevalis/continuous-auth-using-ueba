import { useState } from 'react';
import type { FormEvent } from 'react';
import type { ProviderRegistry } from '@/api/contracts';
import Dropdown from '@/components/ui/Dropdown';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import InlineError from '@/components/ui/InlineError';
import Field from '@/components/ui/Field';
import type { ProviderConnectionView } from './types';

const methodLabels = {
	api_token: 'API token',
	oauth_client_credentials: 'OAuth client credentials',
	service_account: 'Service account',
} as const;

export type ProviderConnectionFormValues = {
	provider_registry_id: string;
	connection_name: string;
	base_url: string;
	auth_realm: string;
	client_id: string;
	client_secret_ref: string;
	api_token_ref: string;
	external_tenant_reference: string;
};

function getInitialValues(
	connection: ProviderConnectionView | undefined,
	providers: ProviderRegistry[],
): ProviderConnectionFormValues {
	return {
		provider_registry_id:
			connection?.provider_registry_id ?? providers[0]?.id ?? '',
		connection_name: connection?.connection_name ?? '',
		base_url: connection?.base_url ?? '',
		auth_realm: connection?.auth_realm ?? '',
		client_id: connection?.client_id ?? '',
		client_secret_ref: connection?.client_secret_ref ?? '',
		api_token_ref: connection?.api_token_ref ?? '',
		external_tenant_reference: connection?.external_tenant_reference ?? '',
	};
}

export default function ProviderConnectionDialog({
	connection,
	providers,
	onClose,
	onSubmit,
	pending,
	error,
}: {
	connection?: ProviderConnectionView;
	providers: ProviderRegistry[];
	onClose: () => void;
	onSubmit: (_values: ProviderConnectionFormValues) => Promise<void>;
	pending: boolean;
	error: Error | null;
}) {
	const [values, setValues] = useState(() =>
		getInitialValues(connection, providers),
	);
	const [validationError, setValidationError] = useState<string | null>(null);
	const editing = !!connection;
	const selectedProvider = providers.find(
		(provider) => provider.id === values.provider_registry_id,
	);
	const method = selectedProvider?.connection_method;

	function updateValue<Key extends keyof ProviderConnectionFormValues>(
		key: Key,
		value: ProviderConnectionFormValues[Key],
	) {
		setValues((current) => ({ ...current, [key]: value }));
	}

	async function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		if (!selectedProvider) {
			setValidationError('Select a provider.');
			return;
		}
		if (!values.connection_name.trim()) {
			setValidationError('Enter a connection name.');
			return;
		}
		if (!values.base_url.trim()) {
			setValidationError('Enter a base URL.');
			return;
		}
		try {
			const url = new URL(values.base_url);
			if (!['http:', 'https:'].includes(url.protocol)) throw new Error();
		} catch {
			setValidationError('Enter a valid HTTP or HTTPS base URL.');
			return;
		}
		if (
			method === 'oauth_client_credentials' &&
			(!values.auth_realm.trim() ||
				!values.client_id.trim() ||
				!values.client_secret_ref.trim())
		) {
			setValidationError(
				'OAuth connections require a realm, client ID, and client secret reference.',
			);
			return;
		}
		if (method === 'api_token' && !values.api_token_ref.trim()) {
			setValidationError('API token connections require a token reference.');
			return;
		}

		setValidationError(null);
		try {
			await onSubmit({
				...values,
				connection_name: values.connection_name.trim(),
				base_url: values.base_url.trim(),
				auth_realm: values.auth_realm.trim(),
				client_id: values.client_id.trim(),
				client_secret_ref: values.client_secret_ref.trim(),
				api_token_ref: values.api_token_ref.trim(),
				external_tenant_reference: values.external_tenant_reference.trim(),
			});
		} catch {
			// The mutation error is rendered while the dialog remains open.
		}
	}

	return (
		<Modal
			eyebrow="Integrations"
			title={editing ? 'Edit response provider' : 'Add response provider'}
			titleId="provider-connection-dialog-title"
			onClose={onClose}
			closeDisabled={pending}
		>
			<form className="grid gap-3" onSubmit={handleSubmit}>
				<div className="grid grid-cols-2 gap-3">
					<Field label="Provider" required className="min-w-0">
						<div className="h-9 rounded-control border border-stone-300">
							<Dropdown
								label="Provider"
								options={providers.map((provider) => ({
									label: provider.display_name,
									value: provider.id,
								}))}
								value={values.provider_registry_id}
								onChange={(value) => updateValue('provider_registry_id', value)}
								fullWidth
								disabled={editing || providers.length === 0}
								buttonClassName="text-sm text-primary"
							/>
						</div>
					</Field>
					<Field label="Connection name" required className="min-w-0">
						<Input
							required
							value={values.connection_name}
							onChange={(event) =>
								updateValue('connection_name', event.target.value)
							}
						/>
					</Field>
				</div>
				<div className="grid grid-cols-2 gap-3">
					<Field label="Base URL" required className="min-w-0">
						<Input
							required
							type="url"
							value={values.base_url}
							onChange={(event) => updateValue('base_url', event.target.value)}
						/>
					</Field>
					<Field label="Connection method" required className="min-w-0">
						<div className="flex h-9 min-w-0 items-center rounded-control border border-stone-300 bg-stone-100 px-3 text-sm text-carbon-700">
							<span className="truncate">
								{method ? methodLabels[method] : 'Select a provider'}
							</span>
						</div>
					</Field>
				</div>
				{(method === 'oauth_client_credentials' ||
					method === 'service_account') && (
					<>
						<Field
							label="Auth realm"
							required={method === 'oauth_client_credentials'}
						>
							<Input
								required={method === 'oauth_client_credentials'}
								value={values.auth_realm}
								onChange={(event) =>
									updateValue('auth_realm', event.target.value)
								}
							/>
						</Field>
						<div className="grid gap-3 sm:grid-cols-2">
							<Field
								label="Client ID"
								required={method === 'oauth_client_credentials'}
							>
								<Input
									required={method === 'oauth_client_credentials'}
									value={values.client_id}
									onChange={(event) =>
										updateValue('client_id', event.target.value)
									}
								/>
							</Field>
							<Field
								label="Client secret reference"
								required={method === 'oauth_client_credentials'}
							>
								<Input
									required={method === 'oauth_client_credentials'}
									value={values.client_secret_ref}
									onChange={(event) =>
										updateValue('client_secret_ref', event.target.value)
									}
								/>
							</Field>
						</div>
					</>
				)}
				{method === 'api_token' && (
					<Field label="API token reference" required>
						<Input
							required
							value={values.api_token_ref}
							onChange={(event) =>
								updateValue('api_token_ref', event.target.value)
							}
						/>
					</Field>
				)}
				<Field
					label={
						<>
							External tenant reference{' '}
							<span className="text-carbon-500">(optional)</span>
						</>
					}
				>
					<Input
						value={values.external_tenant_reference}
						onChange={(event) =>
							updateValue('external_tenant_reference', event.target.value)
						}
					/>
				</Field>
				{(validationError || error) && (
					<InlineError>{validationError ?? error?.message}</InlineError>
				)}
				<div className="mt-1 flex justify-end">
					<Button
						type="submit"
						loading={pending}
						disabled={providers.length === 0}
						className="border-primary"
					>
						{editing ? 'Save' : 'Add'}
					</Button>
				</div>
			</form>
		</Modal>
	);
}
