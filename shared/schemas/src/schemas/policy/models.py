from datetime import datetime
from typing import Any
from uuid import UUID

from domain.policy import PolicyAction, ScoreBand
from pydantic import Field

from schemas.base import SchemaModel


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


class PolicyDecisionCreateSchema(SchemaModel):
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


class PolicyDecisionFilterParams(SchemaModel):
	auth_event_id: UUID | None = None
	decision_band: ScoreBand | None = None
	final_action: PolicyAction | None = None
	decided_after: datetime | None = None
	decided_before: datetime | None = None
	sort: str = '-decided_at'
	limit: int = Field(default=50, ge=1, le=200)
	offset: int = Field(default=0, ge=0)
