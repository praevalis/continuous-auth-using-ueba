import PageHeader from '@/components/ui/PageHeader';

export default function ThreatFeedIntro() {
	return (
		<PageHeader
			eyebrow="Monitor"
			eyebrowTone="caution"
			title="Review sign-in events as they arrive"
			description="Find sign-in activity that needs attention and understand the response decision."
			id="threat-feed-heading"
			trailing={
				<p className="inline-flex min-h-10 items-center rounded-md border border-stone-300 bg-paper-50 px-4 py-2 text-sm leading-5 text-carbon-700 lg:mt-7 lg:max-w-xs">
					Continuous monitoring is active.
				</p>
			}
		/>
	);
}
