import PageLayout from '@/components/layout/PageLayout';

export default function ProviderConnections() {
	return (
		<PageLayout title="Provider connections">
			<section className="mt-8 max-w-2xl">
				<h2 className="text-section-title text-primary">
					Provider connections
				</h2>
				<p className="mt-2 text-sm text-carbon-300">
					Configure provider connections used for response actions.
				</p>
			</section>
		</PageLayout>
	);
}
