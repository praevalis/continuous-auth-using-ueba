import { useCallback, useEffect, useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import AddProviderConnectionDialog from './AddProviderConnectionDialog';
import ProviderConnectionSection from './ProviderConnectionSection';
import ProviderConnectionsIntro from './ProviderConnectionsIntro';
import { api } from '@/api/client';
import { useTenant } from '@/api/tenant';
import type { ProviderConnectionView } from './types';

export default function ProviderConnections() {
	const { tenant } = useTenant();
	const [connections, setConnections] = useState<ProviderConnectionView[]>([]);
	const [providers, setProviders] = useState<
		ProviderConnectionView['provider'][]
	>([]);
	const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const load = useCallback(async () => {
		if (!tenant) return;
		setLoading(true);
		try {
			const [items, registry] = await Promise.all([
				api.listConnections(tenant.id),
				api.listProviders(),
			]);
			setProviders(registry);
			setConnections(
				items
					.map((item) => ({
						...item,
						provider:
							registry.find(
								(provider) => provider.id === item.provider_registry_id,
							) ?? registry[0],
					}))
					.filter((item): item is ProviderConnectionView => !!item.provider),
			);
			setError(null);
		} catch (reason) {
			setError(
				reason instanceof Error
					? reason.message
					: 'Unable to load provider connections',
			);
		} finally {
			setLoading(false);
		}
	}, [tenant]);
	useEffect(() => {
		queueMicrotask(() => void load());
	}, [load]);

	if (loading)
		return (
			<PageLayout title="Response providers">
				<p className="mt-10 text-sm text-carbon-500">
					Loading response providers…
				</p>
			</PageLayout>
		);
	if (error)
		return (
			<PageLayout title="Response providers">
				<p className="mt-10 text-sm text-lockout">{error}</p>
				<button
					className="mt-4 rounded-control border border-primary px-4 py-2 text-sm"
					onClick={() => void load()}
				>
					Retry
				</button>
			</PageLayout>
		);
	return (
		<PageLayout title="Response providers">
			<ProviderConnectionsIntro onAdd={() => setIsAddDialogOpen(true)} />
			<div className="mt-8 lg:mt-16">
				{connections.map((connection) => (
					<ProviderConnectionSection
						key={connection.id}
						connection={connection}
						onTest={() =>
							void api.testConnection(tenant!.id, connection.id).then(load)
						}
						onEdit={() => undefined}
						onToggle={() =>
							void (
								connection.status === 'active'
									? api.disableConnection(tenant!.id, connection.id)
									: api.activateConnection(tenant!.id, connection.id)
							).then(load)
						}
					/>
				))}
			</div>
			{isAddDialogOpen && (
				<AddProviderConnectionDialog
					onClose={() => setIsAddDialogOpen(false)}
					onCreate={async (payload) => {
						await api.createConnection(tenant!.id, {
							...payload,
							provider_registry_id:
								providers[0]?.id ?? payload.provider_registry_id,
						});
						await load();
					}}
				/>
			)}
		</PageLayout>
	);
}
