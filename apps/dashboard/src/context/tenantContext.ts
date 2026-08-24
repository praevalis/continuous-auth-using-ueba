import { createContext } from 'react';
import type { Tenant } from '@/api/contracts';

export type TenantContextValue = {
	tenant: Tenant | null;
	tenants: Tenant[];
	loading: boolean;
	error: string | null;
	refresh: () => Promise<void>;
	setTenantId: (_id: string) => void;
};

export const TenantContext = createContext<TenantContextValue | null>(null);
