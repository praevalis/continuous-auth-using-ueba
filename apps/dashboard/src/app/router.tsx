import { createBrowserRouter } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import Activity from '@/features/activity/Activity';
import Overview from '@/features/overview/Overview';
import Policies from '@/features/policies/Policies';
import ThreatFeed from '@/features/threat-feed/ThreatFeed';

export const router = createBrowserRouter([
	{
		path: '/',
		Component: AppLayout,
		children: [
			{ index: true, Component: Overview, handle: { title: 'Overview' } },
			{ path: 'threat-feed', Component: ThreatFeed, handle: { title: 'Threat feed' } },
			{ path: 'policies', Component: Policies, handle: { title: 'Policies' } },
			{ path: 'activity', Component: Activity, handle: { title: 'Activity' } },
		],
	},
]);
