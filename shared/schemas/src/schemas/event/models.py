from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from domain.event import AuthEventOutcome
from pydantic import Field

from schemas.alert.models import AlertSchema
from schemas.base import SchemaModel
from schemas.enforcement.models import EnforcementActionSchema
from schemas.policy.models import PolicyDecisionSchema
from schemas.scoring.models import (
	EventProcessingRunSchema,
	FeatureSnapshotSchema,
	RiskScoreSchema,
)


class AuthEventSchema(SchemaModel):
	id: UUID
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
	location_country: str | None = None
	location_region: str | None = None
	occurred_hour: int = Field(ge=0, le=23)
	occurred_day_of_week: int = Field(ge=0, le=6)
	hash_key_version: int = Field(ge=1)
	payload_schema_version: int = Field(ge=1)
	raw_payload_redacted: dict[str, Any] | None = None
	normalization_metadata: dict[str, Any] | None = None
	created_at: datetime


class AuthEventIngestionRequestSchema(SchemaModel):
	event_source_id: UUID | None = None
	source_event_id: str | None = Field(default=None, min_length=1)
	occurred_at: datetime
	payload_schema_version: int = Field(default=1, ge=1)
	raw_payload: dict[str, Any]


class AuthEventIngestionAcceptedSchema(SchemaModel):
	tenant_id: UUID
	event_source_id: UUID
	ingestion_credential_id: UUID
	accepted_at: datetime


class AuthEventIngestionMessageSchema(SchemaModel):
	tenant_id: UUID
	event_source_id: UUID
	ingestion_credential_id: UUID
	source_event_id: str | None = None
	occurred_at: datetime
	accepted_at: datetime
	payload_schema_version: int = Field(ge=1)
	raw_payload: dict[str, Any]


class AuthEventCreateSchema(SchemaModel):
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
	location_country: str | None = None
	location_region: str | None = None
	occurred_hour: int = Field(ge=0, le=23)
	occurred_day_of_week: int = Field(ge=0, le=6)
	hash_key_version: int = Field(ge=1)
	payload_schema_version: int = Field(ge=1)
	raw_payload_redacted: dict[str, Any] | None = None
	normalization_metadata: dict[str, Any] | None = None


class AuthEventScoringJobSchema(SchemaModel):
	auth_event_id: UUID
	tenant_id: UUID


class AuthEventListFilterParams(SchemaModel):
	occurred_after: datetime | None = None
	occurred_before: datetime | None = None
	event_source_id: UUID | None = None
	event_type: str | None = Field(default=None, min_length=1)
	outcome: AuthEventOutcome | None = None
	location_country: str | None = Field(default=None, min_length=1)
	sort: str = '-occurred_at'
	limit: int = Field(default=50, ge=1, le=200)
	offset: int = Field(default=0, ge=0)


class AuthEventDetailSchema(SchemaModel):
	"""An authentication event with its persisted processing evidence."""

	event: AuthEventSchema
	processing_run: EventProcessingRunSchema | None = None
	feature_snapshot: FeatureSnapshotSchema | None = None
	risk_score: RiskScoreSchema | None = None
	policy_decision: PolicyDecisionSchema | None = None
	alerts: list[AlertSchema] = Field(default_factory=list)
	enforcement_actions: list[EnforcementActionSchema] = Field(default_factory=list)
