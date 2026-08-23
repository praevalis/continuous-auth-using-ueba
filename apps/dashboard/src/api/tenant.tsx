import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useState,
} from 'react';
import type { ReactNode } from 'react';
import { api } from './client';
import type { Tenant } from './contracts';

type TenantContextValue = {
	tenant: Tenant | null;
	tenants: Tenant[];
	loading: boolean;
	error: string | null;
	refresh: () => Promise<void>;
	setTenantId: (_id: string) => void;
};
const TenantContext = createContext<TenantContextValue | null>(null);

export function TenantProvider({ children }: { children: ReactNode }) {
	const [tenants, setTenants] = useState<Tenant[]>([]);
	const [tenantId, setTenantId] = useState(
		() => localStorage.getItem('tenant-id') ?? '',
	);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const refresh = useCallback(async () => {
		setLoading(true);
		setError(null);
		try {
			const values = await api.listTenants();
			setTenants(values);
			if (!tenantId && values[0]) {
				setTenantId(values[0].id);
				localStorage.setItem('tenant-id', values[0].id);
			}
		} catch (reason) {
			setError(
				reason instanceof Error ? reason.message : 'Unable to load tenants',
			);
		} finally {
			setLoading(false);
		}
	}, [tenantId]);

	useEffect(() => {
		queueMicrotask(() => void refresh());
	}, [refresh]);

	const changeTenant = useCallback((id: string) => {
		setTenantId(id);
		localStorage.setItem('tenant-id', id);
	}, []);
	const value = useMemo(
		() => ({
			tenant:
				tenants.find((item) => item.id === tenantId) ?? tenants[0] ?? null,
			tenants,
			loading,
			error,
			refresh,
			setTenantId: changeTenant,
		}),
		[changeTenant, error, loading, refresh, tenantId, tenants],
	);

	return (
		<TenantContext.Provider value={value}>{children}</TenantContext.Provider>
	);
}

export function useTenant() {
	const value = useContext(TenantContext);
	if (!value) throw new Error('useTenant must be used inside TenantProvider');
	return value;
}
