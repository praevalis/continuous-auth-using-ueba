from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from schemas.base import SchemaModel


class AuthEventOutcome(StrEnum):
	SUCCESS = 'success'
	FAILURE = 'failure'
	CHALLENGE = 'challenge'
	LOGOUT = 'logout'
	UNKNOWN = 'unknown'


class EventLocationSchema(SchemaModel):
	country: str | None = None
	region: str | None = None


class NormalizedAuthEventSchema(SchemaModel):
	tenant_id: UUID
	event_source_id: UUID
	ingestion_credential_id: UUID | None = None
	source_event_id: str | None = None
	idempotency_key: str = Field(min_length=1)
	occurred_at: datetime
	ingested_at: datetime
	event_type: str = Field(min_length=1)
	outcome: AuthEventOutcome
	user_hash: str = Field(min_length=1)
	account_hash: str | None = None
	session_hash: str | None = None
	source_ip_hash: str | None = None
	source_ip_prefix: str | None = None
	device_hash: str | None = None
	host_hash: str | None = None
	auth_method: str | None = None
	failure_reason: str | None = None
	location: EventLocationSchema | None = None
	occurred_hour: int = Field(ge=0, le=23)
	occurred_day_of_week: int = Field(ge=0, le=6)
	hash_key_version: int = Field(ge=1)
	payload_schema_version: int = Field(ge=1)
	raw_payload_redacted: dict[str, Any] | None = None
	normalization_metadata: dict[str, Any] | None = None


class PersistedAuthEventSchema(NormalizedAuthEventSchema):
	id: UUID
	created_at: datetime
