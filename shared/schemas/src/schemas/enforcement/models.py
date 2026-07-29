from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from schemas.base import SchemaModel


class EnforcementActionType(StrEnum):
	STEP_UP_MFA = 'step_up_mfa'
	TERMINATE_SESSION = 'terminate_session'
	LOCK_ACCOUNT = 'lock_account'


class EnforcementActionStatus(StrEnum):
	PENDING = 'pending'
	SENT = 'sent'
	SUCCEEDED = 'succeeded'
	FAILED = 'failed'
	SKIPPED = 'skipped'


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
