from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from domain.enforcement.enums import EnforcementActionStatus, EnforcementActionType


@dataclass(slots=True)
class EnforcementAction:
	id: UUID
	tenant_id: UUID
	policy_decision_id: UUID
	event_source_id: UUID | None
	action_type: EnforcementActionType
	target_user_hash: str
	integration_name: str
	request_payload_redacted: dict[str, Any] | None
	status: EnforcementActionStatus
	attempt_count: int
	external_action_id: str | None
	error_code: str | None
	error_message: str | None
	requested_at: datetime
	completed_at: datetime | None
	created_at: datetime
