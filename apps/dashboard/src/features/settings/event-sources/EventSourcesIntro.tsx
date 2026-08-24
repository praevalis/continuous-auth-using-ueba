import Button from '@/components/ui/Button';
import PageHeader from '@/components/ui/PageHeader';

export default function EventSourcesIntro({ onAdd }: { onAdd: () => void }) {
	return (
		<PageHeader
			eyebrow="Ingestion"
			eyebrowTone="safe"
			title="Manage event sources and credentials"
			description="Configure where authentication events come from and manage the credentials used to send them."
			id="event-sources-heading"
			trailing={
				<Button
					variant="secondary"
					onClick={onAdd}
					className="self-start border-primary lg:mt-1"
				>
					Add event source
				</Button>
			}
		/>
	);
}
