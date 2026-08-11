import { Outlet } from 'react-router-dom';
import TopNavigation from '@/components/layout/TopNavigation';

export default function AppLayout() {
	return (
		<div className="min-h-svh bg-paper-100 text-carbon-700">
			<TopNavigation />
			<Outlet />
		</div>
	);
}
