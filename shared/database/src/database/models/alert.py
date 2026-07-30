from datetime import datetime
from uuid import UUID

from domain.alert import AlertSeverity, AlertStatus
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.base import Base
from database.utils import enum_type


class AlertModel(Base):
	__tablename__ = 'alerts'

	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id'), nullable=False, index=True
	)
	policy_decision_id: Mapped[UUID] = mapped_column(
		ForeignKey('policy_decisions.id'), nullable=False
	)
	risk_score_id: Mapped[UUID] = mapped_column(
		ForeignKey('risk_scores.id'), nullable=False
	)
	severity: Mapped[AlertSeverity] = mapped_column(
		enum_type(AlertSeverity, name='alert_severity'),
		nullable=False,
	)
	status: Mapped[AlertStatus] = mapped_column(
		enum_type(AlertStatus, name='alert_status'),
		nullable=False,
		index=True,
	)
	title: Mapped[str] = mapped_column(String(255), nullable=False)
	summary: Mapped[str] = mapped_column(String(500), nullable=False)
	alert_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONB)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)
	acknowledged_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	resolved_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
