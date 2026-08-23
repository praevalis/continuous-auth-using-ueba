import { useCallback, useEffect, useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import AddEventSourceDialog from './AddEventSourceDialog';
import EventSourceSection from './EventSourceSection';
import EventSourcesIntro from './EventSourcesIntro';
import { api } from '@/api/client';
import { useTenant } from '@/api/tenant';
import type { EventSourceWithCredentials } from './types';

export default function EventSources() {
	const { tenant } = useTenant();
	const [sources, setSources] = useState<EventSourceWithCredentials[]>([]);
	const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const load = useCallback(async () => {
		if (!tenant) return;
		setLoading(true);
		try {
			const values = await api.listEventSources(tenant.id);
			const withCredentials = await Promise.all(
				values.map(async (source) => ({
					...source,
					credentials: await api.listCredentials(tenant.id, source.id),
				})),
			);
			setSources(withCredentials);
			setError(null);
		} catch (reason) {
			setError(
				reason instanceof Error
					? reason.message
					: 'Unable to load event sources',
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
			<PageLayout title="Event sources and credentials">
				<p className="mt-10 text-sm text-carbon-500">Loading event sources…</p>
			</PageLayout>
		);
	if (error)
		return (
			<PageLayout title="Event sources and credentials">
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
		<PageLayout title="Event sources and credentials">
			<EventSourcesIntro onAdd={() => setIsAddDialogOpen(true)} />
			<div className="mt-10">
				{sources.map((source) => (
					<EventSourceSection
						key={source.id}
						source={source}
						onIssueCredential={() =>
							void api
								.issueCredential(tenant!.id, {
									credential_name: `${source.source_name} key`,
									event_source_id: source.id,
									credential_type: 'api_key',
								})
								.then(async (issued) => {
									await navigator.clipboard?.writeText(issued.plaintext_secret);
									await load();
								})
						}
						onEdit={() => undefined}
						onToggle={() =>
							void (
								source.status === 'active'
									? api.disableEventSource(source.id)
									: api.activateEventSource(source.id)
							).then(load)
						}
						onRotate={(credentialId) =>
							void api.rotateCredential(credentialId).then(load)
						}
						onRevoke={(credentialId) =>
							void api.revokeCredential(credentialId).then(load)
						}
					/>
				))}
			</div>
			{isAddDialogOpen && (
				<AddEventSourceDialog
					onClose={() => setIsAddDialogOpen(false)}
					onCreate={async (payload) => {
						await api.createEventSource(tenant!.id, payload);
						await load();
					}}
				/>
			)}
		</PageLayout>
	);
}
