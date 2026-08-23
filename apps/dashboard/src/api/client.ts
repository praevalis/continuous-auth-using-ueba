import type { operations } from './generated/types';
import type {
	AlertListResponse,
	AuthEventDetail,
	AuthEventListResponse,
	EventSource,
	EventSourceCreate,
	EventSourceMetadataUpdate,
	EnforcementActionListResponse,
	IngestionCredential,
	IngestionCredentialCreate,
	IssuedIngestionCredential,
	OperatingMode,
	OperatingModeCreate,
	PolicyDecisionListResponse,
	ProviderConnectionTestResult,
	ProviderRegistry,
	RiskSummary,
	Tenant,
	TenantProviderConnection,
	TenantProviderConnectionCreate,
	TenantUpdate,
	ThresholdProfile,
} from './contracts';

export type ApiError = Error & { status?: number };
const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function request<T>(
	path: string,
	init?: globalThis.RequestInit,
): Promise<T> {
	const response = await fetch(`${baseUrl}${path}`, {
		headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
		...init,
	});

	if (!response.ok) {
		const error = new Error(`Request failed (${response.status})`) as ApiError;
		error.status = response.status;
		try {
			const body = await response.json();
			if (body.detail) error.message = body.detail;
		} catch {
			/* preserve the useful status message */
		}
		throw error;
	}

	if (response.status === 204) return undefined as T;
	return response.json() as Promise<T>;
}

function query(
	params: Record<string, string | number | boolean | null | undefined>,
) {
	const values = Object.entries(params).filter(
		([, value]) => value !== undefined && value !== null && value !== '',
	);
	return values.length
		? `?${new URLSearchParams(values.map(([key, value]) => [key, String(value)]))}`
		: '';
}

export const api = {
	listTenants: () => request<Tenant[]>('/tenants'),

	updateTenant: (id: string, body: TenantUpdate) =>
		request<Tenant>(`/tenants/${id}`, {
			method: 'PATCH',
			body: JSON.stringify(body),
		}),

	listEventSources: (tenantId: string) =>
		request<EventSource[]>(
			`/ingestion/event-sources${query({ tenant_id: tenantId })}`,
		),

	createEventSource: (tenantId: string, body: EventSourceCreate) =>
		request<EventSource>(
			`/ingestion/event-sources${query({ tenant_id: tenantId })}`,
			{ method: 'POST', body: JSON.stringify(body) },
		),

	updateEventSource: (id: string, body: EventSourceMetadataUpdate) =>
		request<EventSource>(`/ingestion/event-sources/${id}`, {
			method: 'PATCH',
			body: JSON.stringify(body),
		}),

	activateEventSource: (id: string) =>
		request<EventSource>(`/ingestion/event-sources/${id}/activate`, {
			method: 'POST',
		}),

	disableEventSource: (id: string) =>
		request<EventSource>(`/ingestion/event-sources/${id}/disable`, {
			method: 'POST',
		}),

	listCredentials: (tenantId: string, eventSourceId?: string) =>
		request<IngestionCredential[]>(
			`/ingestion/ingestion-credentials${query({ tenant_id: tenantId, event_source_id: eventSourceId })}`,
		),

	issueCredential: (tenantId: string, body: IngestionCredentialCreate) =>
		request<IssuedIngestionCredential>(
			`/ingestion/ingestion-credentials${query({ tenant_id: tenantId })}`,
			{ method: 'POST', body: JSON.stringify(body) },
		),

	rotateCredential: (id: string) =>
		request<IssuedIngestionCredential>(
			`/ingestion/ingestion-credentials/${id}/rotate`,
			{ method: 'POST' },
		),

	revokeCredential: (id: string) =>
		request<IngestionCredential>(
			`/ingestion/ingestion-credentials/${id}/revoke`,
			{
				method: 'POST',
			},
		),

	listProviders: () =>
		request<ProviderRegistry[]>(
			'/integrations/provider-registry?is_active=true',
		),

	listConnections: (tenantId: string) =>
		request<TenantProviderConnection[]>(
			`/integrations/tenant-provider-connections${query({ tenant_id: tenantId })}`,
		),

	createConnection: (tenantId: string, body: TenantProviderConnectionCreate) =>
		request<TenantProviderConnection>(
			`/integrations/tenant-provider-connections${query({ tenant_id: tenantId })}`,
			{ method: 'POST', body: JSON.stringify(body) },
		),

	activateConnection: (tenantId: string, id: string) =>
		request<TenantProviderConnection>(
			`/integrations/tenant-provider-connections/${id}/activate${query({ tenant_id: tenantId })}`,
			{ method: 'POST' },
		),

	disableConnection: (tenantId: string, id: string) =>
		request<TenantProviderConnection>(
			`/integrations/tenant-provider-connections/${id}/disable${query({ tenant_id: tenantId })}`,
			{ method: 'POST' },
		),

	testConnection: (tenantId: string, id: string) =>
		request<ProviderConnectionTestResult>(
			`/integrations/tenant-provider-connections/${id}/test${query({ tenant_id: tenantId })}`,
			{ method: 'POST' },
		),

	listEvents: (
		tenantId: string,
		params: operations['list_events_tenants__tenant_id__events_get']['parameters']['query'] = {},
	) =>
		request<AuthEventListResponse>(
			`/tenants/${tenantId}/events${query(params ?? {})}`,
		),

	getEvent: (tenantId: string, id: string) =>
		request<AuthEventDetail>(`/tenants/${tenantId}/events/${id}`),

	getRiskSummary: (
		tenantId: string,
		params: operations['get_risk_summary_tenants__tenant_id__risk_summary_get']['parameters']['query'] = {},
	) =>
		request<RiskSummary>(
			`/tenants/${tenantId}/risk-summary${query(params ?? {})}`,
		),

	listAlerts: (tenantId: string, params = {}) =>
		request<AlertListResponse>(`/tenants/${tenantId}/alerts${query(params)}`),

	listDecisions: (tenantId: string, params = {}) =>
		request<PolicyDecisionListResponse>(
			`/tenants/${tenantId}/policy-decisions${query(params)}`,
		),

	listActions: (tenantId: string, params = {}) =>
		request<EnforcementActionListResponse>(
			`/tenants/${tenantId}/enforcement-actions${query(params)}`,
		),

	listModes: (tenantId: string) =>
		request<OperatingMode[]>(`/tenants/${tenantId}/operating-modes`),

	createMode: (tenantId: string, body: OperatingModeCreate) =>
		request<OperatingMode>(`/tenants/${tenantId}/operating-modes`, {
			method: 'POST',
			body: JSON.stringify(body),
		}),

	listProfiles: (tenantId: string) =>
		request<ThresholdProfile[]>(`/tenants/${tenantId}/threshold-profiles`),
};
