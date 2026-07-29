from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from schemas.base import SchemaModel


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


class IngestionCredentialType(StrEnum):
	API_KEY = 'api_key'


class IngestionCredentialStatus(StrEnum):
	ACTIVE = 'active'
	REVOKED = 'revoked'
	EXPIRED = 'expired'


class TenantSchema(SchemaModel):
	id: UUID
	slug: str = Field(min_length=1)
	display_name: str = Field(min_length=1)
	status: TenantStatus
	default_timezone: str = Field(min_length=1)
	created_at: datetime
	updated_at: datetime


class TenantOperatingModeSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	mode: OperatingMode
	is_active: bool
	effective_from: datetime
	effective_to: datetime | None = None
	changed_by: str | None = None
	change_reason: str | None = None
	created_at: datetime


class TenantThresholdProfileSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	name: str = Field(min_length=1)
	description: str | None = None
	caution_threshold: float
	lockout_threshold: float
	fusion_alpha: float | None = None
	is_active: bool
	effective_from: datetime
	effective_to: datetime | None = None
	created_at: datetime
	updated_at: datetime


class TenantHashKeyVersionSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	key_version: int = Field(ge=1)
	algorithm: str = Field(min_length=1)
	secret_ref: str = Field(min_length=1)
	is_active: bool
	effective_from: datetime
	effective_to: datetime | None = None
	created_at: datetime


class EventSourceSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	source_name: str = Field(min_length=1)
	source_type: EventSourceType
	vendor: str | None = None
	external_reference: str | None = None
	status: EventSourceStatus
	created_at: datetime
	updated_at: datetime


class IngestionCredentialSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	event_source_id: UUID | None = None
	credential_name: str = Field(min_length=1)
	credential_type: IngestionCredentialType
	key_id: str = Field(min_length=1)
	key_hash: str = Field(min_length=1)
	status: IngestionCredentialStatus
	expires_at: datetime | None = None
	last_used_at: datetime | None = None
	created_at: datetime
	rotated_at: datetime | None = None
