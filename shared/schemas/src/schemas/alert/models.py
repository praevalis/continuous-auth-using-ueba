from datetime import datetime
from typing import Any
from uuid import UUID

from domain.alert import AlertSeverity, AlertStatus
from pydantic import Field

from schemas.base import SchemaModel


class AlertSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	policy_decision_id: UUID
	risk_score_id: UUID
	severity: AlertSeverity
	status: AlertStatus
	title: str = Field(min_length=1)
	summary: str = Field(min_length=1)
	alert_metadata: dict[str, Any] | None = None
	created_at: datetime
	acknowledged_at: datetime | None = None
	resolved_at: datetime | None = None
