from datetime import datetime
from uuid import UUID, uuid4

from domain.integration import (
	ProviderConnectionMethod,
	ProviderType,
	TenantProviderConnectionStatus,
)
from domain.policy import PolicyAction
from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.base import Base
from database.utils import enum_type


class ProviderRegistryModel(Base):
	__tablename__ = 'provider_registry'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	provider_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
	display_name: Mapped[str] = mapped_column(String(255), nullable=False)
	provider_type: Mapped[ProviderType] = mapped_column(
		enum_type(ProviderType, name='provider_type'),
		nullable=False,
	)
	connection_method: Mapped[ProviderConnectionMethod] = mapped_column(
		enum_type(ProviderConnectionMethod, name='provider_connection_method'),
		nullable=False,
	)
	supported_policy_actions: Mapped[list[PolicyAction]] = mapped_column(
		JSONB,
		nullable=False,
		default=list,
	)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
	deprecated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		server_default=func.now(),
		onupdate=func.now(),
		nullable=False,
	)

	tenant_connections: Mapped[list['TenantProviderConnectionModel']] = relationship(
		back_populates='provider_registry'
	)


class TenantProviderConnectionModel(Base):
	__tablename__ = 'tenant_provider_connections'
	__table_args__ = (UniqueConstraint('tenant_id', 'connection_name'),)

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True
	)
	provider_registry_id: Mapped[UUID] = mapped_column(
		ForeignKey('provider_registry.id'), nullable=False, index=True
	)
	connection_name: Mapped[str] = mapped_column(String(255), nullable=False)
	base_url: Mapped[str] = mapped_column(String(500), nullable=False)
	auth_realm: Mapped[str | None] = mapped_column(String(255))
	client_id: Mapped[str | None] = mapped_column(String(255))
	client_secret_ref: Mapped[str | None] = mapped_column(String(255))
	api_token_ref: Mapped[str | None] = mapped_column(String(255))
	external_tenant_reference: Mapped[str | None] = mapped_column(String(255))
	status: Mapped[TenantProviderConnectionStatus] = mapped_column(
		enum_type(
			TenantProviderConnectionStatus,
			name='tenant_provider_connection_status',
		),
		nullable=False,
		index=True,
	)
	disabled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	last_tested_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	last_test_error: Mapped[str | None] = mapped_column(String(500))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		server_default=func.now(),
		onupdate=func.now(),
		nullable=False,
	)

	provider_registry: Mapped[ProviderRegistryModel] = relationship(
		back_populates='tenant_connections'
	)
