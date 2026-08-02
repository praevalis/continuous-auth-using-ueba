from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from domain.event import AuthEventOutcome
from schemas.event import AuthEventScoringJobSchema


@dataclass(frozen=True, slots=True)
class AuthEventNormalizedFields:
	"""Canonical auth-event fields derived before anonymization."""

	tenant_id: UUID
	event_source_id: UUID
	ingestion_credential_id: UUID | None
	source_event_id: str | None
	occurred_at: datetime
	ingested_at: datetime
	event_type: str
	outcome: AuthEventOutcome
	user_identifier: str
	account_identifier: str | None
	session_identifier: str | None
	source_ip: str | None
	device_identifier: str | None
	host_identifier: str | None
	auth_method: str | None
	failure_reason: str | None
	location_country: str | None
	location_region: str | None
	occurred_hour: int
	occurred_day_of_week: int
	payload_schema_version: int
	raw_payload: dict[str, Any]
	normalization_metadata: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class AuthEventPersistenceResult:
	"""Describe the newly created auth events from idempotent persistence."""

	created_count: int
	scoring_jobs: list[AuthEventScoringJobSchema]
