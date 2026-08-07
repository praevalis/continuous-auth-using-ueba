from datetime import datetime
from typing import Any
from uuid import UUID

from domain.enforcement import EnforcementActionStatus, EnforcementActionType
from pydantic import Field

from schemas.base import SchemaModel


class EnforcementActionSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	policy_decision_id: UUID
	event_source_id: UUID | None = None
	action_type: EnforcementActionType
	target_user_hash: str = Field(min_length=1)
	integration_name: str = Field(min_length=1)
	request_payload_redacted: dict[str, Any] | None = None
	status: EnforcementActionStatus
	attempt_count: int = Field(ge=0)
	external_action_id: str | None = None
	error_code: str | None = None
	error_message: str | None = None
	requested_at: datetime
	completed_at: datetime | None = None
	created_at: datetime


class EnforcementActionCreateSchema(SchemaModel):
	tenant_id: UUID
	policy_decision_id: UUID
	event_source_id: UUID | None = None
	action_type: EnforcementActionType
	target_user_hash: str = Field(min_length=1)
	integration_name: str = Field(min_length=1)
	request_payload_redacted: dict[str, Any] | None = None
	status: EnforcementActionStatus
	attempt_count: int = Field(ge=0)
	external_action_id: str | None = None
	error_code: str | None = None
	error_message: str | None = None
	requested_at: datetime
	completed_at: datetime | None = None


class EnforcementActionUpdateSchema(SchemaModel):
	event_source_id: UUID | None = None
	request_payload_redacted: dict[str, Any] | None = None
	status: EnforcementActionStatus | None = None
	attempt_count: int | None = Field(default=None, ge=0)
	external_action_id: str | None = None
	error_code: str | None = None
	error_message: str | None = None
	completed_at: datetime | None = None


class EnforcementActionFilterParams(SchemaModel):
	policy_decision_id: UUID | None = None
	event_source_id: UUID | None = None
	action_type: EnforcementActionType | None = None
	integration_name: str | None = Field(default=None, min_length=1)
	status: EnforcementActionStatus | None = None
	requested_after: datetime | None = None
	requested_before: datetime | None = None
	completed_after: datetime | None = None
	completed_before: datetime | None = None
	sort: str = '-requested_at'
	limit: int = Field(default=50, ge=1, le=200)
	offset: int = Field(default=0, ge=0)
