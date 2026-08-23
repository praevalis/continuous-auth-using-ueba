import { useState } from 'react';
import type { FormEvent } from 'react';
import { LuX } from 'react-icons/lu';
import Dropdown from '@/components/ui/Dropdown';
import type { ProviderConnectionMethod } from './types';
import type { components } from '@/api/generated/types';

const methodOptions = [
	{ label: 'OAuth client credentials', value: 'oauth_client_credentials' },
	{ label: 'Service account', value: 'service_account' },
	{ label: 'API token', value: 'api_token' },
];

export default function AddProviderConnectionDialog({
	onClose,
	onCreate,
}: {
	onClose: () => void;
	onCreate: (
		_connection: components['schemas']['TenantProviderConnectionCreateSchema'],
	) => void | Promise<void>;
}) {
	const [name, setName] = useState('');
	const [baseUrl, setBaseUrl] = useState('');
	const [method, setMethod] = useState<ProviderConnectionMethod>(
		'oauth_client_credentials',
	);

	function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		if (!name.trim() || !baseUrl.trim()) return;
		void onCreate({
			provider_registry_id: 'provider-registry-keycloak',
			connection_name: name.trim(),
			base_url: baseUrl.trim(),
			auth_realm: null,
			client_id: null,
			client_secret_ref: null,
			api_token_ref: null,
			external_tenant_reference: null,
			status: 'disabled',
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
				aria-labelledby="add-response-provider-title"
			>
				<div className="flex items-start justify-between gap-4">
					<div>
						<p className="text-label uppercase tracking-[0.12em] text-carbon-300">
							Integrations
						</p>
						<h2
							id="add-response-provider-title"
							className="mt-2 text-xl font-semibold text-primary"
						>
							Add response provider
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
						<span>Provider</span>
						<div className="h-10 rounded-control border border-stone-300">
							<Dropdown
								label="Provider"
								options={[{ label: 'Keycloak', value: 'keycloak' }]}
								value="keycloak"
								fullWidth
								buttonClassName="text-sm text-primary"
							/>
						</div>
					</label>
					<label className="grid gap-2 text-sm text-primary">
						<span>Connection name</span>
						<input
							required
							value={name}
							onChange={(event) => setName(event.target.value)}
							className="h-10 rounded-control border border-stone-300 bg-transparent px-3 text-sm outline-none focus-visible:border-primary"
						/>
					</label>
					<label className="grid gap-2 text-sm text-primary">
						<span>Base URL</span>
						<input
							required
							type="url"
							value={baseUrl}
							onChange={(event) => setBaseUrl(event.target.value)}
							className="h-10 rounded-control border border-stone-300 bg-transparent px-3 text-sm outline-none focus-visible:border-primary"
						/>
					</label>
					<label className="grid gap-2 text-sm text-primary">
						<span>Connection method</span>
						<div className="h-10 rounded-control border border-stone-300">
							<Dropdown
								label="Connection method"
								options={methodOptions}
								value={method}
								onChange={(value) =>
									setMethod(value as ProviderConnectionMethod)
								}
								fullWidth
								buttonClassName="text-sm text-primary"
							/>
						</div>
					</label>
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
							Add response provider
						</button>
					</div>
				</form>
			</div>
		</div>
	);
}
