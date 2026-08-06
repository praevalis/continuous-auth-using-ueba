from datetime import datetime
from uuid import UUID, uuid4

from domain.tenant import (
	EventPayloadFormat,
	EventSourceStatus,
	EventSourceType,
	IngestionCredentialStatus,
	IngestionCredentialType,
	OperatingMode,
	TenantStatus,
)
from sqlalchemy import (
	Boolean,
	Float,
	ForeignKey,
	Integer,
	String,
	UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.base import Base
from database.utils import enum_type


class TenantModel(Base):
	__tablename__ = 'tenants'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
	display_name: Mapped[str] = mapped_column(String(255), nullable=False)
	status: Mapped[TenantStatus] = mapped_column(
		enum_type(TenantStatus, name='tenant_status'),
		nullable=False,
	)
	default_timezone: Mapped[str] = mapped_column(String(100), nullable=False)
	deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		server_default=func.now(),
		onupdate=func.now(),
		nullable=False,
	)

	operating_modes: Mapped[list['TenantOperatingModeModel']] = relationship(
		back_populates='tenant',
		cascade='all, delete-orphan',
		passive_deletes=True,
	)
	threshold_profiles: Mapped[list['TenantThresholdProfileModel']] = relationship(
		back_populates='tenant',
		cascade='all, delete-orphan',
		passive_deletes=True,
	)
	hash_key_versions: Mapped[list['TenantHashKeyVersionModel']] = relationship(
		back_populates='tenant',
		cascade='all, delete-orphan',
		passive_deletes=True,
	)
	event_sources: Mapped[list['EventSourceModel']] = relationship(
		back_populates='tenant',
		cascade='all, delete-orphan',
		passive_deletes=True,
	)
	ingestion_credentials: Mapped[list['IngestionCredentialModel']] = relationship(
		back_populates='tenant',
		cascade='all, delete-orphan',
		passive_deletes=True,
	)


class TenantOperatingModeModel(Base):
	__tablename__ = 'tenant_operating_modes'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True
	)
	mode: Mapped[OperatingMode] = mapped_column(
		enum_type(OperatingMode, name='operating_mode'),
		nullable=False,
	)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	effective_from: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)
	effective_to: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	changed_by: Mapped[str | None] = mapped_column(String(255))
	change_reason: Mapped[str | None] = mapped_column(String(500))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)

	tenant: Mapped[TenantModel] = relationship(back_populates='operating_modes')


class TenantThresholdProfileModel(Base):
	__tablename__ = 'tenant_threshold_profiles'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True
	)
	name: Mapped[str] = mapped_column(String(255), nullable=False)
	description: Mapped[str | None] = mapped_column(String(500))
	caution_threshold: Mapped[float] = mapped_column(Float, nullable=False)
	lockout_threshold: Mapped[float] = mapped_column(Float, nullable=False)
	fusion_alpha: Mapped[float | None] = mapped_column(Float)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	effective_from: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)
	effective_to: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		server_default=func.now(),
		onupdate=func.now(),
		nullable=False,
	)

	tenant: Mapped[TenantModel] = relationship(back_populates='threshold_profiles')


class TenantHashKeyVersionModel(Base):
	__tablename__ = 'tenant_hash_key_versions'
	__table_args__ = (UniqueConstraint('tenant_id', 'key_version'),)

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True
	)
	key_version: Mapped[int] = mapped_column(Integer, nullable=False)
	algorithm: Mapped[str] = mapped_column(String(100), nullable=False)
	salt_value: Mapped[str] = mapped_column(String(255), nullable=False)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	effective_from: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)
	effective_to: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)

	tenant: Mapped[TenantModel] = relationship(back_populates='hash_key_versions')


class EventSourceModel(Base):
	__tablename__ = 'event_sources'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True
	)
	source_name: Mapped[str] = mapped_column(String(255), nullable=False)
	source_type: Mapped[EventSourceType] = mapped_column(
		enum_type(EventSourceType, name='event_source_type'),
		nullable=False,
	)
	payload_format: Mapped[EventPayloadFormat | None] = mapped_column(
		enum_type(EventPayloadFormat, name='event_payload_format')
	)
	vendor: Mapped[str | None] = mapped_column(String(255))
	external_reference: Mapped[str | None] = mapped_column(String(255))
	status: Mapped[EventSourceStatus] = mapped_column(
		enum_type(EventSourceStatus, name='event_source_status'),
		nullable=False,
	)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		server_default=func.now(),
		onupdate=func.now(),
		nullable=False,
	)

	tenant: Mapped[TenantModel] = relationship(back_populates='event_sources')
	ingestion_credentials: Mapped[list['IngestionCredentialModel']] = relationship(
		back_populates='event_source',
		cascade='all, delete-orphan',
		passive_deletes=True,
	)


class IngestionCredentialModel(Base):
	__tablename__ = 'ingestion_credentials'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True
	)
	event_source_id: Mapped[UUID | None] = mapped_column(
		ForeignKey('event_sources.id', ondelete='CASCADE')
	)
	credential_name: Mapped[str] = mapped_column(String(255), nullable=False)
	credential_type: Mapped[IngestionCredentialType] = mapped_column(
		enum_type(IngestionCredentialType, name='ingestion_credential_type'),
		nullable=False,
	)
	key_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
	key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	status: Mapped[IngestionCredentialStatus] = mapped_column(
		enum_type(IngestionCredentialStatus, name='ingestion_credential_status'),
		nullable=False,
	)
	expires_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	last_used_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)
	rotated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

	tenant: Mapped[TenantModel] = relationship(back_populates='ingestion_credentials')
	event_source: Mapped[EventSourceModel | None] = relationship(
		back_populates='ingestion_credentials'
	)
