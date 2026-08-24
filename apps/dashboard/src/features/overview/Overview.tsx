import PageLayout from '@/components/layout/PageLayout';
import { useTenant } from '@/hooks/useTenant';
import Callout from '@/components/ui/Callout';
import ResourceError from '@/components/ui/ResourceError';
import OverviewIntro from './OverviewIntro';
import PlatformStatus from './PlatformStatus';
import RiskLandscape from './RiskLandscape';
import RecentSignInActivity from './RecentSignInActivity';
import WorkToReview from './WorkToReview';
import SystemActivity from './SystemActivity';
import { createOverviewLoadingItems, mapOverviewData } from './adapters';
import { useOverview } from '@/hooks/useOverview';

const loadingReviewItems = [
	{ id: '01', label: 'Caution sign-in decisions', value: '-' },
	{ id: '02', label: 'Lockout decisions', value: '-' },
	{ id: '03', label: 'Analysis still in progress', value: '-' },
	{ id: '04', label: 'Responses skipped in Simulation', value: '-' },
];

const loadingChart = {
	heading: 'Recent activity',
	ariaLabel: 'Recent activity trace',
	labels: [],
	traces: [],
};

export default function Overview() {
	const {
		tenant,
		loading: tenantLoading,
		error: tenantError,
		refresh,
	} = useTenant();
	const overview = useOverview(tenant?.id);
	const view = overview.data ? mapOverviewData(overview.data) : null;
	const loading =
		(tenantLoading || overview.loading || (!!tenant?.id && !overview.data)) &&
		!tenantError &&
		!overview.error;
	const error = tenantError ?? overview.error?.message ?? null;

	return (
		<PageLayout title="Overview">
			<OverviewIntro
				heading="Understand sign-in activity at a glance"
				description="Here is the current state of sign-in activity and responses."
				insight={
					view?.insight ??
					(loading
						? 'Loading current sign-in activity…'
						: 'Overview data is not available.')
				}
				insightDetail={
					view?.insightDetail ??
					(loading
						? 'Loading review focus…'
						: 'Try refreshing to load the latest state.')
				}
			/>

			{error && (
				<ResourceError
					className="mt-8"
					title="Unable to load overview"
					error={error}
					onRetry={() => void (tenantError ? refresh() : overview.refresh())}
				/>
			)}

			<PlatformStatus
				heading="Platform status"
				items={view?.platformItems ?? createOverviewLoadingItems()}
				loading={loading}
			/>
			<RiskLandscape
				heading="Risk landscape"
				segments={view?.riskSegments ?? []}
				chart={view?.chart ?? loadingChart}
				loading={loading}
			/>
			<section
				className="mt-14 grid gap-10 lg:grid-cols-[1.2fr_0.8fr]"
				aria-label="Activity review"
			>
				<RecentSignInActivity
					items={view?.recentActivity ?? []}
					loading={loading}
				/>
				<WorkToReview
					heading="Work to review"
					items={view?.reviewItems ?? loadingReviewItems}
					loading={loading}
				/>
				<div className="lg:col-span-2">
					<Callout title="Main signal">
						<p>
							{view?.mainSignal ?? (loading ? 'Loading review focus…' : '—')}
						</p>
					</Callout>
				</div>
			</section>
			<SystemActivity
				heading="System activity"
				items={view?.systemActivity ?? []}
				loading={loading}
			/>
		</PageLayout>
	);
}
