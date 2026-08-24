import { useContext } from 'react';
import { TenantContext } from '@/context/tenantContext';

export function useTenant() {
	const value = useContext(TenantContext);
	if (!value) throw new Error('useTenant must be used inside TenantProvider');
	return value;
}
