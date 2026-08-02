from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from schemas.tenant import (
	TenantHashKeyVersionCreateSchema,
	TenantHashKeyVersionFilterParams,
	TenantHashKeyVersionRetireSchema,
	TenantHashKeyVersionSchema,
	TenantOperatingModeCreateSchema,
	TenantOperatingModeFilterParams,
	TenantOperatingModeRetireSchema,
	TenantOperatingModeSchema,
	TenantThresholdProfileCreateSchema,
	TenantThresholdProfileFilterParams,
	TenantThresholdProfileRetireSchema,
	TenantThresholdProfileSchema,
)

from api.dependencies import get_tenant_configuration_service
from api.services.tenants import TenantConfigurationService

router = APIRouter(prefix='/tenants/{tenant_id}', tags=['tenant-configuration'])


@router.post(
	'/operating-modes',
	response_model=TenantOperatingModeSchema,
	status_code=status.HTTP_201_CREATED,
)
async def create_operating_mode(
	tenant_id: UUID,
	payload: TenantOperatingModeCreateSchema,
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> TenantOperatingModeSchema:
	"""Create an operating mode for a tenant.

	Args:
		tenant_id: The tenant identifier.
		payload: The operating mode payload.
		service: The tenant configuration service.

	Returns:
		The created operating mode.
	"""
	return await service.create_operating_mode(tenant_id, payload)


@router.get('/operating-modes', response_model=list[TenantOperatingModeSchema])
async def list_operating_modes(
	tenant_id: UUID,
	filters: Annotated[TenantOperatingModeFilterParams, Depends()],
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> list[TenantOperatingModeSchema]:
	"""Return operating modes for a tenant.

	Args:
		tenant_id: The tenant identifier.
		filters: The operating mode filter parameters.
		service: The tenant configuration service.

	Returns:
		The operating modes for the tenant.
	"""
	return await service.list_operating_modes(tenant_id, filters)


@router.get(
	'/operating-modes/{operating_mode_id}',
	response_model=TenantOperatingModeSchema,
)
async def get_operating_mode(
	tenant_id: UUID,
	operating_mode_id: UUID,
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> TenantOperatingModeSchema:
	"""Return an operating mode for a tenant.

	Args:
		tenant_id: The tenant identifier.
		operating_mode_id: The operating mode identifier.
		service: The tenant configuration service.

	Returns:
		The matching operating mode.
	"""
	return await service.get_operating_mode(tenant_id, operating_mode_id)


@router.post(
	'/operating-modes/{operating_mode_id}/retire',
	response_model=TenantOperatingModeSchema,
)
async def retire_operating_mode(
	tenant_id: UUID,
	operating_mode_id: UUID,
	payload: TenantOperatingModeRetireSchema,
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> TenantOperatingModeSchema:
	"""Retire an operating mode for a tenant.

	Args:
		tenant_id: The tenant identifier.
		operating_mode_id: The operating mode identifier.
		payload: The operating mode retirement payload.
		service: The tenant configuration service.

	Returns:
		The retired operating mode.
	"""
	return await service.retire_operating_mode(tenant_id, operating_mode_id, payload)


@router.post(
	'/threshold-profiles',
	response_model=TenantThresholdProfileSchema,
	status_code=status.HTTP_201_CREATED,
)
async def create_threshold_profile(
	tenant_id: UUID,
	payload: TenantThresholdProfileCreateSchema,
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> TenantThresholdProfileSchema:
	"""Create a threshold profile for a tenant.

	Args:
		tenant_id: The tenant identifier.
		payload: The threshold profile payload.
		service: The tenant configuration service.

	Returns:
		The created threshold profile.
	"""
	return await service.create_threshold_profile(tenant_id, payload)


@router.get('/threshold-profiles', response_model=list[TenantThresholdProfileSchema])
async def list_threshold_profiles(
	tenant_id: UUID,
	filters: Annotated[TenantThresholdProfileFilterParams, Depends()],
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> list[TenantThresholdProfileSchema]:
	"""Return threshold profiles for a tenant.

	Args:
		tenant_id: The tenant identifier.
		filters: The threshold profile filter parameters.
		service: The tenant configuration service.

	Returns:
		The threshold profiles for the tenant.
	"""
	return await service.list_threshold_profiles(tenant_id, filters)


@router.get(
	'/threshold-profiles/{threshold_profile_id}',
	response_model=TenantThresholdProfileSchema,
)
async def get_threshold_profile(
	tenant_id: UUID,
	threshold_profile_id: UUID,
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> TenantThresholdProfileSchema:
	"""Return a threshold profile for a tenant.

	Args:
		tenant_id: The tenant identifier.
		threshold_profile_id: The threshold profile identifier.
		service: The tenant configuration service.

	Returns:
		The matching threshold profile.
	"""
	return await service.get_threshold_profile(tenant_id, threshold_profile_id)


@router.post(
	'/threshold-profiles/{threshold_profile_id}/retire',
	response_model=TenantThresholdProfileSchema,
)
async def retire_threshold_profile(
	tenant_id: UUID,
	threshold_profile_id: UUID,
	payload: TenantThresholdProfileRetireSchema,
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> TenantThresholdProfileSchema:
	"""Retire a threshold profile for a tenant.

	Args:
		tenant_id: The tenant identifier.
		threshold_profile_id: The threshold profile identifier.
		payload: The threshold profile retirement payload.
		service: The tenant configuration service.

	Returns:
		The retired threshold profile.
	"""
	return await service.retire_threshold_profile(
		tenant_id,
		threshold_profile_id,
		payload,
	)


@router.post(
	'/hash-key-versions',
	response_model=TenantHashKeyVersionSchema,
	status_code=status.HTTP_201_CREATED,
)
async def create_hash_key_version(
	tenant_id: UUID,
	payload: TenantHashKeyVersionCreateSchema,
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> TenantHashKeyVersionSchema:
	"""Create a hash key version for a tenant.

	Args:
		tenant_id: The tenant identifier.
		payload: The hash key version payload.
		service: The tenant configuration service.

	Returns:
		The created hash key version.
	"""
	return await service.create_hash_key_version(tenant_id, payload)


@router.get('/hash-key-versions', response_model=list[TenantHashKeyVersionSchema])
async def list_hash_key_versions(
	tenant_id: UUID,
	filters: Annotated[TenantHashKeyVersionFilterParams, Depends()],
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> list[TenantHashKeyVersionSchema]:
	"""Return hash key versions for a tenant.

	Args:
		tenant_id: The tenant identifier.
		filters: The hash key version filter parameters.
		service: The tenant configuration service.

	Returns:
		The hash key versions for the tenant.
	"""
	return await service.list_hash_key_versions(tenant_id, filters)


@router.get(
	'/hash-key-versions/{hash_key_version_id}',
	response_model=TenantHashKeyVersionSchema,
)
async def get_hash_key_version(
	tenant_id: UUID,
	hash_key_version_id: UUID,
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> TenantHashKeyVersionSchema:
	"""Return a hash key version for a tenant.

	Args:
		tenant_id: The tenant identifier.
		hash_key_version_id: The hash key version identifier.
		service: The tenant configuration service.

	Returns:
		The matching hash key version.
	"""
	return await service.get_hash_key_version(tenant_id, hash_key_version_id)


@router.post(
	'/hash-key-versions/{hash_key_version_id}/retire',
	response_model=TenantHashKeyVersionSchema,
)
async def retire_hash_key_version(
	tenant_id: UUID,
	hash_key_version_id: UUID,
	payload: TenantHashKeyVersionRetireSchema,
	service: Annotated[
		TenantConfigurationService, Depends(get_tenant_configuration_service)
	],
) -> TenantHashKeyVersionSchema:
	"""Retire a hash key version for a tenant.

	Args:
		tenant_id: The tenant identifier.
		hash_key_version_id: The hash key version identifier.
		payload: The hash key version retirement payload.
		service: The tenant configuration service.

	Returns:
		The retired hash key version.
	"""
	return await service.retire_hash_key_version(
		tenant_id,
		hash_key_version_id,
		payload,
	)
