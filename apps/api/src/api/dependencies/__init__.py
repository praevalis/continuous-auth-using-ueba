"""API dependency providers package."""

from api.dependencies.cache import get_cache_manager, get_redis_client
from api.dependencies.database import (
	get_database_manager,
	get_db_session,
	get_session_manager,
	get_unit_of_work,
)
from api.dependencies.event_broker import get_event_broker_manager
from api.dependencies.infrastructure import get_infrastructure_manager
from api.dependencies.services import (
	get_auth_event_ingestion_service,
	get_event_source_service,
	get_ingestion_credential_service,
	get_tenant_configuration_service,
	get_tenant_management_service,
	get_tenant_onboarding_service,
)

__all__ = [
	'get_auth_event_ingestion_service',
	'get_cache_manager',
	'get_database_manager',
	'get_db_session',
	'get_event_broker_manager',
	'get_event_source_service',
	'get_infrastructure_manager',
	'get_ingestion_credential_service',
	'get_redis_client',
	'get_session_manager',
	'get_tenant_configuration_service',
	'get_tenant_management_service',
	'get_tenant_onboarding_service',
	'get_unit_of_work',
]
