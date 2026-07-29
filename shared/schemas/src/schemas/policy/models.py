from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from schemas.base import SchemaModel


class ScoreBand(StrEnum):
	SAFE = 'safe'
	CAUTION = 'caution'
	LOCKOUT = 'lockout'


class PolicyAction(StrEnum):
	ALLOW = 'allow'
	STEP_UP_MFA = 'step_up_mfa'
	TERMINATE_SESSION = 'terminate_session'
	LOCK_ACCOUNT = 'lock_account'
	ALERT_ONLY = 'alert_only'
	NONE = 'none'


class PolicyDecisionSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	auth_event_id: UUID
	risk_score_id: UUID
	operating_mode_id: UUID
	decision_band: ScoreBand
	recommended_action: PolicyAction
	final_action: PolicyAction
	decision_reason: str | None = None
	decision_metadata: dict[str, Any] | None = None
	decided_at: datetime
