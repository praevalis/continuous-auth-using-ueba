from datetime import datetime
from uuid import UUID

from domain.event import AuthEventOutcome
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.base import Base
from database.utils import enum_type


class AuthEventModel(Base):
	__tablename__ = 'auth_events'
	__table_args__ = (UniqueConstraint('tenant_id', 'idempotency_key'),)

	id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id'), nullable=False, index=True
	)
	event_source_id: Mapped[UUID] = mapped_column(
		ForeignKey('event_sources.id'), nullable=False, index=True
	)
	ingestion_credential_id: Mapped[UUID | None] = mapped_column(
		ForeignKey('ingestion_credentials.id')
	)
	source_event_id: Mapped[str | None] = mapped_column(String(255))
	idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
	occurred_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False, index=True
	)
	ingested_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)
	event_type: Mapped[str] = mapped_column(String(100), nullable=False)
	outcome: Mapped[AuthEventOutcome] = mapped_column(
		enum_type(AuthEventOutcome, name='auth_event_outcome'),
		nullable=False,
	)
	user_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
	account_hash: Mapped[str | None] = mapped_column(String(255))
	session_hash: Mapped[str | None] = mapped_column(String(255))
	source_ip_hash: Mapped[str | None] = mapped_column(String(255))
	source_ip_prefix: Mapped[str | None] = mapped_column(String(50))
	device_hash: Mapped[str | None] = mapped_column(String(255))
	host_hash: Mapped[str | None] = mapped_column(String(255), index=True)
	auth_method: Mapped[str | None] = mapped_column(String(100))
	failure_reason: Mapped[str | None] = mapped_column(String(255))
	location_country: Mapped[str | None] = mapped_column(String(100))
	location_region: Mapped[str | None] = mapped_column(String(100))
	occurred_hour: Mapped[int] = mapped_column(Integer, nullable=False)
	occurred_day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
	hash_key_version: Mapped[int] = mapped_column(Integer, nullable=False)
	payload_schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
	raw_payload_redacted: Mapped[dict[str, object] | None] = mapped_column(JSONB)
	normalization_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONB)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)
