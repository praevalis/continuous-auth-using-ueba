import { useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import EmptyState from '@/components/ui/EmptyState';
import ResourceError from '@/components/ui/ResourceError';
import { useTenant } from '@/hooks/useTenant';
import type {
	TenantProviderConnectionCreate,
	TenantProviderConnectionUpdate,
} from '@/api/contracts';
import { useProviderConnectionMutation, useProviderConnections } from '@/hooks';
import ProviderConnectionDialog, {
	type ProviderConnectionFormValues,
} from './ProviderConnectionDialog';
import ProviderConnectionSection, {
	ProviderConnectionSectionSkeleton,
} from './ProviderConnectionSection';
import ProviderConnectionsIntro from './ProviderConnectionsIntro';

export default function ProviderConnections() {
	const {
		tenant,
		loading: tenantLoading,
		error: tenantError,
		refresh: refreshTenant,
	} = useTenant();
	const resource = useProviderConnections(tenant?.id);
	const mutations = useProviderConnectionMutation(tenant?.id);
	const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
	const [editingConnectionId, setEditingConnectionId] = useState<string | null>(
		null,
	);
	const loading = tenantLoading || resource.loading;
	const error = tenantError ?? resource.error?.message ?? null;
	const connections = resource.data?.connections ?? [];
	const providers = resource.data?.providers ?? [];
	const editingConnection = connections.find(
		(connection) => connection.id === editingConnectionId,
	);
	const actionError = mutations.test.error ?? mutations.setStatus.error;

	async function refreshConnections() {
		await resource.refresh();
	}

	async function handleCreate(values: ProviderConnectionFormValues) {
		const body: TenantProviderConnectionCreate = {
			...values,
			provider_registry_id: values.provider_registry_id,
			auth_realm: values.auth_realm || null,
			client_id: values.client_id || null,
			client_secret_ref: values.client_secret_ref || null,
			api_token_ref: values.api_token_ref || null,
			external_tenant_reference: values.external_tenant_reference || null,
			status: 'disabled',
		};
		await mutations.create.mutateAsync(body);
		setIsAddDialogOpen(false);
		await refreshConnections();
	}

	async function handleUpdate(values: ProviderConnectionFormValues) {
		if (!editingConnection) return;
		const body: TenantProviderConnectionUpdate = {
			connection_name: values.connection_name,
			base_url: values.base_url,
			auth_realm: values.auth_realm || null,
			client_id: values.client_id || null,
			client_secret_ref: values.client_secret_ref || null,
			api_token_ref: values.api_token_ref || null,
			external_tenant_reference: values.external_tenant_reference || null,
		};
		await mutations.update.mutateAsync({ id: editingConnection.id, body });
		setEditingConnectionId(null);
		await refreshConnections();
	}

	async function handleTest(connectionId: string) {
		try {
			await mutations.test.mutateAsync(connectionId);
			await refreshConnections();
		} catch {
			// The mutation error is rendered above the connection list.
		}
	}

	async function handleToggle(connectionId: string, active: boolean) {
		try {
			await mutations.setStatus.mutateAsync({ id: connectionId, active });
			await refreshConnections();
		} catch {
			// The mutation error is rendered above the connection list.
		}
	}

	function retry() {
		return tenantError ? refreshTenant() : refreshConnections();
	}

	return (
		<PageLayout title="Response providers">
			<ProviderConnectionsIntro onAdd={() => setIsAddDialogOpen(true)} />
			{error && (
				<ResourceError
					className="mt-8"
					title="Unable to load response providers"
					error={error}
					onRetry={() => void retry()}
				/>
			)}
			{actionError && !error && (
				<ResourceError
					className="mt-6"
					title="Provider action failed"
					error={actionError}
				/>
			)}
			<div className="mt-8 lg:mt-16">
				{loading ? (
					<>
						<ProviderConnectionSectionSkeleton />
						<ProviderConnectionSectionSkeleton />
					</>
				) : error ? null : connections.length > 0 ? (
					connections.map((connection) => (
						<ProviderConnectionSection
							key={connection.id}
							connection={connection}
							busy={mutations.test.pending || mutations.setStatus.pending}
							onTest={() => void handleTest(connection.id)}
							onEdit={() => setEditingConnectionId(connection.id)}
							onToggle={() =>
								void handleToggle(connection.id, connection.status !== 'active')
							}
						/>
					))
				) : (
					<EmptyState title="No response providers configured">
						Add a provider connection to enable automated response actions.
					</EmptyState>
				)}
			</div>
			{isAddDialogOpen && (
				<ProviderConnectionDialog
					providers={providers}
					onClose={() => setIsAddDialogOpen(false)}
					onSubmit={handleCreate}
					pending={mutations.create.pending}
					error={mutations.create.error}
				/>
			)}
			{editingConnection && (
				<ProviderConnectionDialog
					connection={editingConnection}
					providers={providers}
					onClose={() => setEditingConnectionId(null)}
					onSubmit={handleUpdate}
					pending={mutations.update.pending}
					error={mutations.update.error}
				/>
			)}
		</PageLayout>
	);
}
