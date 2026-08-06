from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from schemas.integration import (
	ProviderConnectionTestResultSchema,
	ProviderRegistryCreateSchema,
	ProviderRegistryFilterParams,
	ProviderRegistrySchema,
	ProviderRegistryUpdateSchema,
	TenantProviderConnectionCreateSchema,
	TenantProviderConnectionFilterParams,
	TenantProviderConnectionSchema,
	TenantProviderConnectionUpdateSchema,
)

from api.dependencies import (
	get_provider_registry_service,
	get_tenant_provider_connection_service,
)
from api.services.integrations import (
	ProviderRegistryService,
	TenantProviderConnectionService,
)

router = APIRouter(prefix='/integrations', tags=['integrations'])


@router.post(
	'/provider-registry',
	response_model=ProviderRegistrySchema,
	status_code=status.HTTP_201_CREATED,
)
async def create_provider_registry(
	payload: ProviderRegistryCreateSchema,
	service: Annotated[ProviderRegistryService, Depends(get_provider_registry_service)],
) -> ProviderRegistrySchema:
	"""Create a provider registry entry."""
	return await service.create_provider_registry(payload)


@router.get('/provider-registry', response_model=list[ProviderRegistrySchema])
async def list_provider_registry_entries(
	filters: Annotated[ProviderRegistryFilterParams, Depends()],
	service: Annotated[ProviderRegistryService, Depends(get_provider_registry_service)],
) -> list[ProviderRegistrySchema]:
	"""Return provider registry entries."""
	return await service.list_provider_registry_entries(filters)


@router.get(
	'/provider-registry/{provider_registry_id}',
	response_model=ProviderRegistrySchema,
)
async def get_provider_registry(
	provider_registry_id: UUID,
	service: Annotated[ProviderRegistryService, Depends(get_provider_registry_service)],
) -> ProviderRegistrySchema:
	"""Return a provider registry entry by identifier."""
	return await service.get_provider_registry(provider_registry_id)


@router.patch(
	'/provider-registry/{provider_registry_id}',
	response_model=ProviderRegistrySchema,
)
async def update_provider_registry(
	provider_registry_id: UUID,
	payload: ProviderRegistryUpdateSchema,
	service: Annotated[ProviderRegistryService, Depends(get_provider_registry_service)],
) -> ProviderRegistrySchema:
	"""Update a provider registry entry by identifier."""
	return await service.update_provider_registry(provider_registry_id, payload)


@router.post(
	'/provider-registry/{provider_registry_id}/deprecate',
	response_model=ProviderRegistrySchema,
)
async def deprecate_provider_registry(
	provider_registry_id: UUID,
	service: Annotated[ProviderRegistryService, Depends(get_provider_registry_service)],
) -> ProviderRegistrySchema:
	"""Deprecate a provider registry entry."""
	return await service.deprecate_provider_registry(provider_registry_id)


@router.post(
	'/provider-registry/{provider_registry_id}/reactivate',
	response_model=ProviderRegistrySchema,
)
async def reactivate_provider_registry(
	provider_registry_id: UUID,
	service: Annotated[ProviderRegistryService, Depends(get_provider_registry_service)],
) -> ProviderRegistrySchema:
	"""Reactivate a provider registry entry."""
	return await service.reactivate_provider_registry(provider_registry_id)


@router.post(
	'/tenant-provider-connections',
	response_model=TenantProviderConnectionSchema,
	status_code=status.HTTP_201_CREATED,
)
async def create_tenant_provider_connection(
	tenant_id: Annotated[UUID, Query()],
	payload: TenantProviderConnectionCreateSchema,
	service: Annotated[
		TenantProviderConnectionService,
		Depends(get_tenant_provider_connection_service),
	],
) -> TenantProviderConnectionSchema:
	"""Create a tenant provider connection."""
	return await service.create_tenant_provider_connection(tenant_id, payload)


@router.get(
	'/tenant-provider-connections',
	response_model=list[TenantProviderConnectionSchema],
)
async def list_tenant_provider_connections(
	tenant_id: Annotated[UUID, Query()],
	filters: Annotated[TenantProviderConnectionFilterParams, Depends()],
	service: Annotated[
		TenantProviderConnectionService,
		Depends(get_tenant_provider_connection_service),
	],
) -> list[TenantProviderConnectionSchema]:
	"""Return tenant provider connections for a tenant."""
	return await service.list_tenant_provider_connections(tenant_id, filters)


@router.get(
	'/tenant-provider-connections/{tenant_provider_connection_id}',
	response_model=TenantProviderConnectionSchema,
)
async def get_tenant_provider_connection(
	tenant_id: Annotated[UUID, Query()],
	tenant_provider_connection_id: UUID,
	service: Annotated[
		TenantProviderConnectionService,
		Depends(get_tenant_provider_connection_service),
	],
) -> TenantProviderConnectionSchema:
	"""Return a tenant provider connection by identifier."""
	return await service.get_tenant_provider_connection(
		tenant_id,
		tenant_provider_connection_id,
	)


@router.patch(
	'/tenant-provider-connections/{tenant_provider_connection_id}',
	response_model=TenantProviderConnectionSchema,
)
async def update_tenant_provider_connection(
	tenant_id: Annotated[UUID, Query()],
	tenant_provider_connection_id: UUID,
	payload: TenantProviderConnectionUpdateSchema,
	service: Annotated[
		TenantProviderConnectionService,
		Depends(get_tenant_provider_connection_service),
	],
) -> TenantProviderConnectionSchema:
	"""Update a tenant provider connection by identifier."""
	return await service.update_tenant_provider_connection(
		tenant_id,
		tenant_provider_connection_id,
		payload,
	)


@router.post(
	'/tenant-provider-connections/{tenant_provider_connection_id}/activate',
	response_model=TenantProviderConnectionSchema,
)
async def activate_tenant_provider_connection(
	tenant_id: Annotated[UUID, Query()],
	tenant_provider_connection_id: UUID,
	service: Annotated[
		TenantProviderConnectionService,
		Depends(get_tenant_provider_connection_service),
	],
) -> TenantProviderConnectionSchema:
	"""Activate a tenant provider connection."""
	return await service.activate_tenant_provider_connection(
		tenant_id,
		tenant_provider_connection_id,
	)


@router.post(
	'/tenant-provider-connections/{tenant_provider_connection_id}/disable',
	response_model=TenantProviderConnectionSchema,
)
async def disable_tenant_provider_connection(
	tenant_id: Annotated[UUID, Query()],
	tenant_provider_connection_id: UUID,
	service: Annotated[
		TenantProviderConnectionService,
		Depends(get_tenant_provider_connection_service),
	],
) -> TenantProviderConnectionSchema:
	"""Disable a tenant provider connection."""
	return await service.disable_tenant_provider_connection(
		tenant_id,
		tenant_provider_connection_id,
	)


@router.post(
	'/tenant-provider-connections/{tenant_provider_connection_id}/test',
	response_model=ProviderConnectionTestResultSchema,
)
async def test_tenant_provider_connection(
	tenant_id: Annotated[UUID, Query()],
	tenant_provider_connection_id: UUID,
	service: Annotated[
		TenantProviderConnectionService,
		Depends(get_tenant_provider_connection_service),
	],
) -> ProviderConnectionTestResultSchema:
	"""Test a tenant provider connection."""
	return await service.test_tenant_provider_connection(
		tenant_id,
		tenant_provider_connection_id,
	)
