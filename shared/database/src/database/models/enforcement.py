from datetime import datetime
from uuid import UUID, uuid4

from domain.enforcement import EnforcementActionStatus, EnforcementActionType
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.base import Base
from database.utils import JsonObject, enum_type


class EnforcementActionModel(Base):
	__tablename__ = 'enforcement_actions'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id'), nullable=False, index=True
	)
	policy_decision_id: Mapped[UUID] = mapped_column(
		ForeignKey('policy_decisions.id'), nullable=False
	)
	event_source_id: Mapped[UUID | None] = mapped_column(ForeignKey('event_sources.id'))
	action_type: Mapped[EnforcementActionType] = mapped_column(
		enum_type(EnforcementActionType, name='enforcement_action_type'),
		nullable=False,
	)
	target_user_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	integration_name: Mapped[str] = mapped_column(String(255), nullable=False)
	request_payload_redacted: Mapped[JsonObject | None] = mapped_column(JSONB)
	status: Mapped[EnforcementActionStatus] = mapped_column(
		enum_type(EnforcementActionStatus, name='enforcement_action_status'),
		nullable=False,
		index=True,
	)
	attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	external_action_id: Mapped[str | None] = mapped_column(String(255))
	error_code: Mapped[str | None] = mapped_column(String(100))
	error_message: Mapped[str | None] = mapped_column(String(500))
	requested_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False, index=True
	)
	completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)
