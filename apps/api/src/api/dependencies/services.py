from typing import Annotated

from database import IUnitOfWork
from event_broker import IEventBrokerManager
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import ApiSettings, get_api_settings
from api.dependencies.database import get_db_session, get_unit_of_work
from api.dependencies.event_broker import get_event_broker_manager
from api.services.activity_trends import ActivityTrendReadService
from api.services.alerts import AlertReadService
from api.services.enforcement import EnforcementReadService
from api.services.events import AuthEventReadService
from api.services.ingestion import (
	AuthEventIngestionService,
	EventSourceService,
	IngestionCredentialService,
)
from api.services.integrations import (
	ProviderRegistryService,
	TenantProviderConnectionService,
)
from api.services.pipeline_health import PipelineHealthReadService
from api.services.policy_decisions import PolicyDecisionReadService
from api.services.risk_summary import RiskSummaryReadService
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


def get_auth_event_read_service(
	session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthEventReadService:
	"""Return the auth-event read service.

	Args:
		session: The request-scoped async database session.

	Returns:
		The auth-event read service bound to the current session.
	"""
	return AuthEventReadService(session)


def get_alert_read_service(
	session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AlertReadService:
	"""Return the alert read service.

	Args:
		session: The request-scoped async database session.

	Returns:
		The alert read service bound to the current session.
	"""
	return AlertReadService(session)


def get_enforcement_read_service(
	session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnforcementReadService:
	"""Return the enforcement read service.

	Args:
		session: The request-scoped async database session.

	Returns:
		The enforcement read service bound to the current session.
	"""
	return EnforcementReadService(session)


def get_policy_decision_read_service(
	session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PolicyDecisionReadService:
	"""Return the policy-decision read service.

	Args:
		session: The request-scoped async database session.

	Returns:
		The policy-decision read service bound to the current session.
	"""
	return PolicyDecisionReadService(session)


def get_risk_summary_read_service(
	session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RiskSummaryReadService:
	"""Return the tenant risk-summary read service."""
	return RiskSummaryReadService(session)


def get_activity_trend_read_service(
	session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ActivityTrendReadService:
	"""Return the tenant activity-trend read service.

	Args:
		session: The request-scoped async database session.

	Returns:
		The activity-trend service bound to the current session.
	"""
	return ActivityTrendReadService(session)


def get_pipeline_health_read_service(
	session: Annotated[AsyncSession, Depends(get_db_session)],
	settings: Annotated[ApiSettings, Depends(get_api_settings)],
) -> PipelineHealthReadService:
	"""Return the tenant pipeline-health read service.

	Args:
		session: The request-scoped async database session.
		settings: The API runtime settings containing health thresholds.

	Returns:
		The pipeline-health service bound to the current session.
	"""
	return PipelineHealthReadService(
		session,
		stale_after_minutes=settings.PIPELINE_HEALTH_STALE_AFTER_MINUTES,
		failure_lookback_hours=settings.PIPELINE_HEALTH_FAILURE_LOOKBACK_HOURS,
	)
