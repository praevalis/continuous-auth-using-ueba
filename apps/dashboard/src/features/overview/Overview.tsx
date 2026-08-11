import PageLayout from '@/components/layout/PageLayout';
import OverviewIntro from './OverviewIntro';
import PlatformStatus from './PlatformStatus';
import RiskLandscape from './RiskLandscape';
import RecentSignInActivity from './RecentSignInActivity';
import WorkToReview from './WorkToReview';
import SystemActivity from './SystemActivity';
import Callout from '@/components/ui/Callout';
import { LuDownload, LuSearch, LuShieldCheck } from 'react-icons/lu';

const recentActivity = [
	{
		time: '09:24:31',
		initials: 'JD',
		user: 'j••••@example.com',
		login: 'Okta SSO',
		result: 'Success',
		risk: 'Safe',
		score: '0.21',
		tone: 'safe',
	},
	{
		time: '09:20:17',
		initials: 'LB',
		user: 'l••••@example.com',
		login: 'Azure AD',
		result: 'Success',
		risk: 'Caution',
		score: '0.65',
		tone: 'caution',
	},
	{
		time: '09:18:42',
		initials: 'RP',
		user: 'r••••@example.com',
		login: 'Okta SSO',
		result: 'Failed',
		risk: 'Lockout',
		score: '0.82',
		tone: 'lockout',
	},
	{
		time: '09:15:09',
		initials: 'AT',
		user: 'a••••@example.com',
		login: 'Okta SSO',
		result: 'Failed',
		risk: 'Lockout',
		score: '0.93',
		tone: 'lockout',
	},
];

const reviewItems = [
	{ id: '01', label: 'Caution sign-in decisions', value: '7' },
	{ id: '02', label: 'Lockout decisions', value: '3' },
	{ id: '03', label: 'Analysis still in progress', value: '2' },
	{ id: '04', label: 'Responses skipped in Simulation', value: '0' },
];

const platformItems = [
	{
		icon: LuDownload,
		label: 'Event intake',
		status: 'Healthy',
		updated: 'Updated 5s ago',
	},
	{
		icon: LuSearch,
		label: 'Analysis',
		status: 'Healthy',
		updated: 'Updated 8s ago',
	},
	{
		icon: LuShieldCheck,
		label: 'Responses',
		status: 'Healthy',
		updated: 'Updated 6s ago',
	},
];

const riskSegments = [
	{ label: 'Safe', value: '72%', className: 'bg-safe', tone: 'text-safe' },
	{
		label: 'Caution',
		value: '18%',
		className: 'bg-caution',
		tone: 'text-caution',
	},
	{
		label: 'Lockout',
		value: '10%',
		className: 'bg-lockout',
		tone: 'text-lockout',
	},
];

const activityChart = {
	heading: 'Recent activity',
	ariaLabel: 'Recent activity trace',
	labels: ['Earlier', 'Recent', 'Now'],
	traces: [
		{
			path: 'M0 29 C25 33 30 23 54 29 S84 21 104 28 S130 19 153 26 S181 31 202 27 S232 36 254 26 S283 26 302 30',
			color: '#667A68',
		},
		{
			path: 'M302 30 C324 23 334 34 350 27 S381 30 398 21 S425 31 445 27 S473 34 490 21 S514 32 530 23',
			color: '#A87528',
		},
		{
			path: 'M530 23 C548 30 554 16 566 20 S580 5 592 17 S605 7 616 20 S630 18 640 21',
			color: '#984A43',
		},
	],
};

const systemActivity = [
	{
		id: 'received',
		icon: LuDownload,
		label: 'Sign-in received',
		time: '09:24:31',
		meta: 'Just now',
	},
	{
		id: 'analysis',
		icon: LuSearch,
		label: 'Analysis completed',
		time: '09:24:33',
		meta: 'Just now',
	},
	{
		id: 'alert',
		icon: LuShieldCheck,
		label: 'Alert recorded',
		time: '09:24:33',
		meta: 'Just now',
	},
	{
		id: 'skipped',
		icon: LuShieldCheck,
		label: 'Response skipped',
		time: '09:24:33',
		meta: 'Just now',
	},
];

export default function Overview() {
	return (
		<PageLayout title="Overview">
			<OverviewIntro
				heading="Understand sign-in activity at a glance"
				description="Here is the current state of sign-in activity and responses."
				insight="Sign-in activity is steady;"
				insightDetail="12 decisions need review."
			/>
			<PlatformStatus heading="Platform status" items={platformItems} />
			<RiskLandscape
				heading="Risk landscape"
				segments={riskSegments}
				chart={activityChart}
			/>
			<section
				className="mt-14 grid gap-10 lg:grid-cols-[1.2fr_0.8fr]"
				aria-label="Activity review"
			>
				<RecentSignInActivity items={recentActivity} />
				<WorkToReview heading="Work to review" items={reviewItems} />
				<div className="lg:col-span-2">
					<Callout title="Main signal">
						<p>Caution decisions are the current review focus</p>
					</Callout>
				</div>
			</section>
			<SystemActivity heading="System activity" items={systemActivity} />
		</PageLayout>
	);
}
