import type { components } from './generated/types';

/** Application aliases for the generated OpenAPI contracts. */
export type Tenant = components['schemas']['TenantSchema'];
export type TenantUpdate = components['schemas']['TenantUpdateSchema'];
export type EventSource = components['schemas']['EventSourceSchema'];
export type EventSourceCreate =
	components['schemas']['EventSourceCreateSchema'];
export type EventSourceMetadataUpdate =
	components['schemas']['EventSourceMetadataUpdateSchema'];
export type IngestionCredential =
	components['schemas']['IngestionCredentialSchema'];
export type IngestionCredentialCreate =
	components['schemas']['IngestionCredentialCreateSchema'];
export type IssuedIngestionCredential =
	components['schemas']['IssuedIngestionCredentialSchema'];
export type ProviderRegistry = components['schemas']['ProviderRegistrySchema'];
export type TenantProviderConnection =
	components['schemas']['TenantProviderConnectionSchema'];
export type TenantProviderConnectionCreate =
	components['schemas']['TenantProviderConnectionCreateSchema'];
export type ProviderConnectionTestResult =
	components['schemas']['ProviderConnectionTestResultSchema'];
export type AuthEvent = components['schemas']['AuthEventSchema'];
export type AuthEventListItem =
	components['schemas']['AuthEventListItemSchema'];
export type AuthEventDetail = components['schemas']['AuthEventDetailSchema'];
export type AuthEventListResponse =
	components['schemas']['AuthEventListResponseSchema'];
export type EventProcessingRun =
	components['schemas']['EventProcessingRunSchema'];
export type FeatureSnapshot = components['schemas']['FeatureSnapshotSchema'];
export type Alert = components['schemas']['AlertSchema'];
export type AlertListResponse =
	components['schemas']['AlertListResponseSchema'];
export type PolicyDecision = components['schemas']['PolicyDecisionSchema'];
export type PolicyDecisionListResponse =
	components['schemas']['PolicyDecisionListResponseSchema'];
export type EnforcementAction =
	components['schemas']['EnforcementActionSchema'];
export type EnforcementActionListResponse =
	components['schemas']['EnforcementActionListResponseSchema'];
export type OperatingMode = components['schemas']['TenantOperatingModeSchema'];
export type OperatingModeCreate =
	components['schemas']['TenantOperatingModeCreateSchema'];
export type ThresholdProfile =
	components['schemas']['TenantThresholdProfileSchema'];
export type ThresholdProfileCreate =
	components['schemas']['TenantThresholdProfileCreateSchema'];
export type OperatingModeValue = components['schemas']['OperatingMode'];
export type ProviderConnectionMethod =
	components['schemas']['ProviderConnectionMethod'];
export type RiskSummary = components['schemas']['RiskSummarySchema'];
export type RiskScore = components['schemas']['RiskScoreSchema'];
export type RiskScoreSummary = components['schemas']['RiskScoreSummarySchema'];
