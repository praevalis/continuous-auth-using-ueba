from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from domain.policy.enums import PolicyAction, ScoreBand


@dataclass(slots=True)
class PolicyDecision:
	id: UUID
	tenant_id: UUID
	auth_event_id: UUID
	risk_score_id: UUID
	operating_mode_id: UUID
	decision_band: ScoreBand
	recommended_action: PolicyAction
	final_action: PolicyAction
	decision_reason: str | None
	decision_metadata: dict[str, Any] | None
	decided_at: datetime
