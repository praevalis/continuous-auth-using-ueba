import { useState } from 'react';
import { LuRefreshCw } from 'react-icons/lu';
import PageLayout from '@/components/layout/PageLayout';
import { useTenant } from '@/api/tenant';
import type {
	EventSourceCreate,
	EventSourceMetadataUpdate,
} from '@/api/contracts';
import { useEventSourceMutation, useEventSources } from '@/hooks';
import EventSourceDialog, {
	type EventSourceFormValues,
} from './EventSourceDialog';
import EventSourceSection, {
	EventSourceSectionSkeleton,
} from './EventSourceSection';
import CredentialSecretDialog from './CredentialSecretDialog';
import EventSourcesIntro from './EventSourcesIntro';

export default function EventSources() {
	const {
		tenant,
		loading: tenantLoading,
		error: tenantError,
		refresh: refreshTenant,
	} = useTenant();
	const sourceResource = useEventSources(tenant?.id);
	const mutations = useEventSourceMutation(tenant?.id);
	const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
	const [editingSourceId, setEditingSourceId] = useState<string | null>(null);
	const [issuedSecret, setIssuedSecret] = useState<string | null>(null);
	const loading = tenantLoading || sourceResource.loading;
	const error = tenantError ?? sourceResource.error?.message ?? null;
	const sources = sourceResource.data ?? [];
	const editingSource = sources.find((source) => source.id === editingSourceId);
	const actionError =
		mutations.setStatus.error ??
		mutations.issueCredential.error ??
		mutations.rotateCredential.error ??
		mutations.revokeCredential.error;

	async function refreshSources() {
		await sourceResource.refresh();
	}

	async function handleCreate(values: EventSourceFormValues) {
		const body: EventSourceCreate = {
			...values,
			vendor: values.vendor || null,
			external_reference: values.external_reference || null,
			status: 'active',
		};
		await mutations.create.mutateAsync(body);
		setIsAddDialogOpen(false);
		await refreshSources();
	}

	async function handleUpdate(values: EventSourceFormValues) {
		if (!editingSource) return;
		const body: EventSourceMetadataUpdate = {
			...values,
			vendor: values.vendor || null,
			external_reference: values.external_reference || null,
		};
		await mutations.update.mutateAsync({ id: editingSource.id, body });
		setEditingSourceId(null);
		await refreshSources();
	}

	async function handleIssueCredential(sourceId: string, sourceName: string) {
		try {
			const issued = await mutations.issueCredential.mutateAsync({
				credential_name: `${sourceName} key`,
				event_source_id: sourceId,
				credential_type: 'api_key',
			});
			setIssuedSecret(issued.plaintext_secret);
			await refreshSources();
		} catch {
			// The mutation error is rendered above the source list.
		}
	}

	async function handleToggle(sourceId: string, active: boolean) {
		try {
			await mutations.setStatus.mutateAsync({ id: sourceId, active });
			await refreshSources();
		} catch {
			// The mutation error is rendered above the source list.
		}
	}

	async function handleRotate(credentialId: string) {
		try {
			const issued = await mutations.rotateCredential.mutateAsync(credentialId);
			setIssuedSecret(issued.plaintext_secret);
			await refreshSources();
		} catch {
			// The mutation error is rendered above the source list.
		}
	}

	async function handleRevoke(credentialId: string) {
		try {
			await mutations.revokeCredential.mutateAsync(credentialId);
			await refreshSources();
		} catch {
			// The mutation error is rendered above the source list.
		}
	}

	return (
		<PageLayout title="Event sources and credentials">
			<EventSourcesIntro onAdd={() => setIsAddDialogOpen(true)} />
			{error && (
				<section
					className="mt-8 rounded-panel border border-lockout/30 bg-lockout-soft/30 px-5 py-4 sm:px-6"
					role="alert"
				>
					<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
						<div className="min-w-0">
							<h2 className="text-base font-semibold text-lockout">
								Unable to load event sources
							</h2>
							<p className="mt-1 text-sm text-carbon-700">{error}</p>
						</div>
						<button
							type="button"
							className="inline-flex shrink-0 items-center gap-1.5 self-start rounded-control border border-primary px-3 py-1.5 text-sm text-primary transition hover:bg-primary-soft sm:self-auto"
							onClick={() =>
								tenantError ? void refreshTenant() : void refreshSources()
							}
						>
							<LuRefreshCw size={14} aria-hidden="true" />
							Retry
						</button>
					</div>
				</section>
			)}
			{actionError && !error && (
				<p className="mt-6 text-sm text-lockout" role="alert">
					{actionError.message}
				</p>
			)}
			<div className="mt-10">
				{loading ? (
					<>
						<EventSourceSectionSkeleton />
						<EventSourceSectionSkeleton />
					</>
				) : error ? null : sources.length > 0 ? (
					sources.map((source) => (
						<EventSourceSection
							key={source.id}
							source={source}
							onIssueCredential={() =>
								void handleIssueCredential(source.id, source.source_name)
							}
							onEdit={() => setEditingSourceId(source.id)}
							onToggle={() =>
								void handleToggle(source.id, source.status !== 'active')
							}
							onRotate={(credentialId) => void handleRotate(credentialId)}
							onRevoke={(credentialId) => void handleRevoke(credentialId)}
						/>
					))
				) : (
					<section className="py-10">
						<h2 className="text-lg font-semibold text-primary">
							No event sources configured
						</h2>
						<p className="mt-2 max-w-xl text-sm text-carbon-500">
							Add an event source to begin receiving authentication events.
						</p>
					</section>
				)}
			</div>
			{isAddDialogOpen && (
				<EventSourceDialog
					onClose={() => setIsAddDialogOpen(false)}
					onSubmit={handleCreate}
					pending={mutations.create.pending}
					error={mutations.create.error}
				/>
			)}
			{editingSource && (
				<EventSourceDialog
					source={editingSource}
					onClose={() => setEditingSourceId(null)}
					onSubmit={handleUpdate}
					pending={mutations.update.pending}
					error={mutations.update.error}
				/>
			)}
			{issuedSecret && (
				<CredentialSecretDialog
					secret={issuedSecret}
					onClose={() => setIssuedSecret(null)}
				/>
			)}
		</PageLayout>
	);
}
