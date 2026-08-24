import { LuClock3 } from 'react-icons/lu';
import PageHeader from '@/components/ui/PageHeader';

export default function ActivityIntro({
	loading = false,
}: {
	loading?: boolean;
}) {
	return (
		<PageHeader
			eyebrow="Audit"
			eyebrowTone="lockout"
			title="Trace what the platform recorded and carried out"
			description="Follow analysis, decisions, alerts, and response actions across the tenant."
			id="activity-heading"
			className="gap-5"
			trailing={
				<p className="inline-flex min-h-10 items-center gap-2 self-start rounded-md border border-stone-300 px-4 py-2 text-sm text-carbon-300 lg:mt-7">
					<LuClock3 size={16} aria-hidden="true" />
					{loading ? 'Loading activity' : 'Live activity'}
				</p>
			}
		/>
	);
}
