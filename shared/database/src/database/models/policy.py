from datetime import datetime
from uuid import UUID

from domain.policy import PolicyAction, ScoreBand
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from database.utils import enum_type


class PolicyDecisionModel(Base):
	__tablename__ = 'policy_decisions'

	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id'), nullable=False, index=True
	)
	auth_event_id: Mapped[UUID] = mapped_column(
		ForeignKey('auth_events.id'), nullable=False, index=True
	)
	risk_score_id: Mapped[UUID] = mapped_column(
		ForeignKey('risk_scores.id'), nullable=False
	)
	operating_mode_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenant_operating_modes.id'), nullable=False
	)
	decision_band: Mapped[ScoreBand] = mapped_column(
		enum_type(ScoreBand, name='policy_decision_band'),
		nullable=False,
	)
	recommended_action: Mapped[PolicyAction] = mapped_column(
		enum_type(PolicyAction, name='policy_action'),
		nullable=False,
	)
	final_action: Mapped[PolicyAction] = mapped_column(
		enum_type(PolicyAction, name='policy_final_action'),
		nullable=False,
	)
	decision_reason: Mapped[str | None] = mapped_column(String(500))
	decision_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONB)
	decided_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False, index=True
	)
