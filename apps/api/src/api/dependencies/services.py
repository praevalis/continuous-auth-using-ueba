from typing import Annotated

from database import IUnitOfWork
from fastapi import Depends

from api.dependencies.database import get_unit_of_work
from api.services.ingestion import (
	EventSourceService,
	IngestionCredentialService,
)
from api.services.tenants import (
	TenantConfigurationService,
	TenantManagementService,
	TenantOnboardingService,
)


def get_tenant_onboarding_service(
	uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> TenantOnboardingService:
	"""Return the tenant onboarding application service.

	Args:
		uow: The request-scoped database unit of work.

	Returns:
		The tenant onboarding service bound to the current unit of work.
	"""
	return TenantOnboardingService(uow)


def get_tenant_management_service(
	uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> TenantManagementService:
	"""Return the tenant management application service.

	Args:
		uow: The request-scoped database unit of work.

	Returns:
		The tenant management service bound to the current unit of work.
	"""
	return TenantManagementService(uow)


def get_tenant_configuration_service(
	uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> TenantConfigurationService:
	"""Return the tenant configuration application service.

	Args:
		uow: The request-scoped database unit of work.

	Returns:
		The tenant configuration service bound to the current unit of work.
	"""
	return TenantConfigurationService(uow)


def get_event_source_service(
	uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> EventSourceService:
	"""Return the event source application service.

	Args:
		uow: The request-scoped database unit of work.

	Returns:
		The event source service bound to the current unit of work.
	"""
	return EventSourceService(uow)


def get_ingestion_credential_service(
	uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> IngestionCredentialService:
	"""Return the ingestion credential application service.

	Args:
		uow: The request-scoped database unit of work.

	Returns:
		The ingestion credential service bound to the current unit of work.
	"""
	return IngestionCredentialService(uow)
