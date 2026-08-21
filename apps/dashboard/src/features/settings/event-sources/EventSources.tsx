import PageLayout from '@/components/layout/PageLayout';

export default function EventSources() {
	return (
		<PageLayout title="Event sources and credentials">
			<section className="mt-8 max-w-2xl">
				<h2 className="text-section-title text-primary">
					Event sources and credentials
				</h2>
				<p className="mt-2 text-sm text-carbon-300">
					Configure event sources and manage the credentials used for ingestion.
				</p>
			</section>
		</PageLayout>
	);
}
