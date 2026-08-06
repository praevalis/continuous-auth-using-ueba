from datetime import datetime
from typing import Any
from uuid import UUID

from domain.integration import (
	ProviderConnectionMethod,
	ProviderType,
	TenantProviderConnectionStatus,
)
from domain.policy import PolicyAction
from pydantic import Field

from schemas.base import SchemaModel


class ProviderRegistrySchema(SchemaModel):
	id: UUID
	provider_key: str = Field(min_length=1)
	display_name: str = Field(min_length=1)
	provider_type: ProviderType
	connection_method: ProviderConnectionMethod
	supported_policy_actions: list[PolicyAction]
	is_active: bool
	deprecated_at: datetime | None = None
	created_at: datetime
	updated_at: datetime


class ProviderRegistryCreateSchema(SchemaModel):
	provider_key: str = Field(min_length=1)
	display_name: str = Field(min_length=1)
	provider_type: ProviderType
	connection_method: ProviderConnectionMethod
	supported_policy_actions: list[PolicyAction] = Field(default_factory=list)
	is_active: bool = True
	deprecated_at: datetime | None = None


class ProviderRegistryUpdateSchema(SchemaModel):
	display_name: str | None = Field(default=None, min_length=1)
	connection_method: ProviderConnectionMethod | None = None
	supported_policy_actions: list[PolicyAction] | None = None
	is_active: bool | None = None
	deprecated_at: datetime | None = None


class ProviderRegistryFilterParams(SchemaModel):
	provider_type: ProviderType | None = None
	connection_method: ProviderConnectionMethod | None = None
	is_active: bool | None = None


class TenantProviderConnectionSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	provider_registry_id: UUID
	connection_name: str = Field(min_length=1)
	base_url: str = Field(min_length=1)
	auth_realm: str | None = None
	client_id: str | None = None
	client_secret_ref: str | None = None
	api_token_ref: str | None = None
	external_tenant_reference: str | None = None
	status: TenantProviderConnectionStatus
	disabled_at: datetime | None = None
	last_tested_at: datetime | None = None
	last_test_error: str | None = None
	created_at: datetime
	updated_at: datetime


class TenantProviderConnectionCreateSchema(SchemaModel):
	provider_registry_id: UUID
	connection_name: str = Field(min_length=1)
	base_url: str = Field(min_length=1)
	auth_realm: str | None = None
	client_id: str | None = None
	client_secret_ref: str | None = None
	api_token_ref: str | None = None
	external_tenant_reference: str | None = None
	status: TenantProviderConnectionStatus = TenantProviderConnectionStatus.DISABLED
	disabled_at: datetime | None = None
	last_tested_at: datetime | None = None
	last_test_error: str | None = None


class TenantProviderConnectionUpdateSchema(SchemaModel):
	connection_name: str | None = Field(default=None, min_length=1)
	base_url: str | None = Field(default=None, min_length=1)
	auth_realm: str | None = None
	client_id: str | None = None
	client_secret_ref: str | None = None
	api_token_ref: str | None = None
	external_tenant_reference: str | None = None
	status: TenantProviderConnectionStatus | None = None
	disabled_at: datetime | None = None
	last_tested_at: datetime | None = None
	last_test_error: str | None = None


class TenantProviderConnectionFilterParams(SchemaModel):
	provider_registry_id: UUID | None = None
	status: TenantProviderConnectionStatus | None = None


class ProviderConnectionTestResultSchema(SchemaModel):
	connection_id: UUID
	provider_registry_id: UUID
	provider_key: str = Field(min_length=1)
	success: bool
	tested_at: datetime
	status: TenantProviderConnectionStatus
	error_code: str | None = None
	error_message: str | None = None
	response_metadata: dict[str, Any] | None = None
