import { LuPlus } from 'react-icons/lu';
import Button from '@/components/ui/Button';
import PageHeader from '@/components/ui/PageHeader';

export default function ProviderConnectionsIntro({
	onAdd,
}: {
	onAdd: () => void;
}) {
	return (
		<PageHeader
			eyebrow="Integrations"
			eyebrowTone="caution"
			title="Response providers"
			description="Configure the services used to deliver automated response actions."
			id="response-providers-heading"
			trailing={
				<Button
					variant="secondary"
					onClick={onAdd}
					leading={<LuPlus size={17} aria-hidden="true" />}
					className="self-start lg:mt-1"
				>
					Add response provider
				</Button>
			}
		/>
	);
}
