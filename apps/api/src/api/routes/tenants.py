from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from schemas.onboarding import TenantOnboardingCreateSchema, TenantOnboardingSchema
from schemas.tenant import TenantFilterParams, TenantSchema, TenantUpdateSchema

from api.dependencies import (
	get_tenant_management_service,
	get_tenant_onboarding_service,
)
from api.services.tenants import (
	TenantManagementService,
	TenantOnboardingService,
)

router = APIRouter(prefix='/tenants', tags=['tenants'])


@router.post(
	'',
	response_model=TenantOnboardingSchema,
	status_code=status.HTTP_201_CREATED,
)
async def create_tenant(
	payload: TenantOnboardingCreateSchema,
	service: Annotated[TenantOnboardingService, Depends(get_tenant_onboarding_service)],
) -> TenantOnboardingSchema:
	"""Create a tenant and its initial bootstrap configuration.

	Args:
		payload: The tenant onboarding payload.
		service: The tenant onboarding service.

	Returns:
		The created tenant and its initial active configuration records.
	"""
	return await service.create_tenant(payload)


@router.get('', response_model=list[TenantSchema])
async def list_tenants(
	filters: Annotated[TenantFilterParams, Depends()],
	service: Annotated[TenantManagementService, Depends(get_tenant_management_service)],
) -> list[TenantSchema]:
	"""Return tenants matching the provided filters.

	Args:
		filters: The tenant filter parameters.
		service: The tenant management service.

	Returns:
		The matching tenants.
	"""
	return await service.list_tenants(filters)


@router.get('/{tenant_id}', response_model=TenantSchema)
async def get_tenant(
	tenant_id: UUID,
	service: Annotated[TenantManagementService, Depends(get_tenant_management_service)],
) -> TenantSchema:
	"""Return an active tenant by identifier.

	Args:
		tenant_id: The tenant identifier.
		service: The tenant management service.

	Returns:
		The matching tenant.
	"""
	return await service.get_tenant(tenant_id)


@router.patch('/{tenant_id}', response_model=TenantSchema)
async def update_tenant(
	tenant_id: UUID,
	payload: TenantUpdateSchema,
	service: Annotated[TenantManagementService, Depends(get_tenant_management_service)],
) -> TenantSchema:
	"""Update an active tenant.

	Args:
		tenant_id: The tenant identifier.
		payload: The tenant update payload.
		service: The tenant management service.

	Returns:
		The updated tenant.
	"""
	return await service.update_tenant(tenant_id, payload)


@router.delete('/{tenant_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
	tenant_id: UUID,
	service: Annotated[TenantManagementService, Depends(get_tenant_management_service)],
) -> Response:
	"""Soft delete an active tenant.

	Args:
		tenant_id: The tenant identifier.
		service: The tenant management service.

	Returns:
		An empty response.
	"""
	await service.delete_tenant(tenant_id)
	return Response(status_code=status.HTTP_204_NO_CONTENT)
