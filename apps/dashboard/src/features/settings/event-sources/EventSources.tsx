import { useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import AddEventSourceDialog from './AddEventSourceDialog';
import EventSourceSection from './EventSourceSection';
import EventSourcesIntro from './EventSourcesIntro';
import { mockEventSources } from './mock-data';

export default function EventSources() {
	const [sources, setSources] = useState(mockEventSources);
	const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

	const updateSource = (
		sourceId: string,
		update: (_source: (typeof sources)[number]) => (typeof sources)[number],
	) => {
		setSources((current) =>
			current.map((source) =>
				source.id === sourceId ? update(source) : source,
			),
		);
	};

	return (
		<PageLayout title="Event sources and credentials">
			<EventSourcesIntro onAdd={() => setIsAddDialogOpen(true)} />
			<div className="mt-10">
				{sources.map((source) => (
					<EventSourceSection
						key={source.id}
						source={source}
						onIssueCredential={() => undefined}
						onEdit={() => undefined}
						onToggle={() =>
							updateSource(source.id, (current) => ({
								...current,
								status: current.status === 'active' ? 'disabled' : 'active',
							}))
						}
						onRotate={() => undefined}
						onRevoke={(credentialId) =>
							updateSource(source.id, (current) => ({
								...current,
								credentials: current.credentials.map((credential) =>
									credential.id === credentialId
										? { ...credential, status: 'revoked' }
										: credential,
								),
							}))
						}
					/>
				))}
			</div>
			{isAddDialogOpen && (
				<AddEventSourceDialog
					onClose={() => setIsAddDialogOpen(false)}
					onCreate={(source) => setSources((current) => [...current, source])}
				/>
			)}
		</PageLayout>
	);
}
