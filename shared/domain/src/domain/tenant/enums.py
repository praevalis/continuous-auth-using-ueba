from enum import StrEnum


class TenantStatus(StrEnum):
	ACTIVE = 'active'
	SUSPENDED = 'suspended'
	ARCHIVED = 'archived'


class OperatingMode(StrEnum):
	SHADOW = 'shadow'
	ALERT_ONLY = 'alert_only'
	ENFORCE = 'enforce'


class EventSourceType(StrEnum):
	IDP = 'idp'
	SIEM = 'siem'
	AGENT = 'agent'
	MANUAL_REPLAY = 'manual_replay'


class EventSourceStatus(StrEnum):
	ACTIVE = 'active'
	DISABLED = 'disabled'


class PipelineComponent(StrEnum):
	INGESTION = 'ingestion'
	ANALYSIS = 'analysis'
	RESPONSES = 'responses'


class PipelineHealthStatus(StrEnum):
	HEALTHY = 'healthy'
	DEGRADED = 'degraded'
	IDLE = 'idle'
	NOT_CONFIGURED = 'not_configured'


class EventPayloadFormat(StrEnum):
	JSON = 'json'
	SYSLOG = 'syslog'


class IngestionCredentialType(StrEnum):
	API_KEY = 'api_key'


class IngestionCredentialStatus(StrEnum):
	ACTIVE = 'active'
	REVOKED = 'revoked'
	EXPIRED = 'expired'
