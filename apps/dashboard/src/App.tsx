import { RouterProvider } from 'react-router-dom';
import { router } from '@/app/router';
import { TenantProvider } from '@/api/tenant';

function App() {
	return (
		<TenantProvider>
			<RouterProvider router={router} />
		</TenantProvider>
	);
}

export default App;
