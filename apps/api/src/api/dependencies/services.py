from typing import Annotated

from database import IUnitOfWork
from event_broker import IEventBrokerManager
from fastapi import Depends

from api.core.config import ApiSettings, get_api_settings
from api.dependencies.database import get_unit_of_work
from api.dependencies.event_broker import get_event_broker_manager
from api.services.ingestion import (
	AuthEventIngestionService,
	EventSourceService,
	IngestionCredentialService,
)
from api.services.integrations import (
	ProviderRegistryService,
	TenantProviderConnectionService,
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


def get_auth_event_ingestion_service(
	uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
	event_broker_manager: Annotated[
		IEventBrokerManager, Depends(get_event_broker_manager)
	],
	settings: Annotated[ApiSettings, Depends(get_api_settings)],
) -> AuthEventIngestionService:
	"""Return the auth-event ingestion application service.

	Args:
		uow: The request-scoped database unit of work.
		event_broker_manager: The shared event broker manager.
		settings: The API settings for the current runtime.

	Returns:
		The auth-event ingestion service bound to the current unit of work.
	"""
	return AuthEventIngestionService(
		uow,
		event_broker_manager,
		settings.AUTH_EVENT_INGESTION_STREAM_NAME,
	)


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


def get_provider_registry_service(
	uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> ProviderRegistryService:
	"""Return the provider registry application service.

	Args:
		uow: The request-scoped database unit of work.

	Returns:
		The provider registry service bound to the current unit of work.
	"""
	return ProviderRegistryService(uow)


def get_tenant_provider_connection_service(
	uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> TenantProviderConnectionService:
	"""Return the tenant provider connection application service.

	Args:
		uow: The request-scoped database unit of work.

	Returns:
		The tenant provider connection service bound to the current unit of work.
	"""
	return TenantProviderConnectionService(uow)
