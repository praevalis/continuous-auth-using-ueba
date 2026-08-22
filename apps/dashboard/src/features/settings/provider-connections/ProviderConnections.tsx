import { useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import AddProviderConnectionDialog from './AddProviderConnectionDialog';
import ProviderConnectionSection from './ProviderConnectionSection';
import ProviderConnectionsIntro from './ProviderConnectionsIntro';
import { mockProviderConnections } from './mock-data';
import type { ProviderConnectionView } from './types';

export default function ProviderConnections() {
	const [connections, setConnections] = useState(mockProviderConnections);
	const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

	const updateConnection = (
		connectionId: string,
		update: (_connection: ProviderConnectionView) => ProviderConnectionView,
	) => {
		setConnections((current) =>
			current.map((connection) =>
				connection.id === connectionId ? update(connection) : connection,
			),
		);
	};

	return (
		<PageLayout title="Response providers">
			<ProviderConnectionsIntro onAdd={() => setIsAddDialogOpen(true)} />
			<div className="mt-8 lg:mt-16">
				{connections.map((connection) => (
					<ProviderConnectionSection
						key={connection.id}
						connection={connection}
						onTest={() =>
							updateConnection(connection.id, (current) => ({
								...current,
								status: 'active',
								last_tested_at: new Date().toISOString(),
								last_test_error: null,
							}))
						}
						onEdit={() => undefined}
						onToggle={() =>
							updateConnection(connection.id, (current) => ({
								...current,
								status: current.status === 'active' ? 'disabled' : 'active',
								disabled_at:
									current.status === 'active' ? new Date().toISOString() : null,
							}))
						}
					/>
				))}
			</div>
			{isAddDialogOpen && (
				<AddProviderConnectionDialog
					onClose={() => setIsAddDialogOpen(false)}
					onCreate={(connection) =>
						setConnections((current) => [...current, connection])
					}
				/>
			)}
		</PageLayout>
	);
}
