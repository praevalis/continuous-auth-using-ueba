"""Shared database package."""

from database.base import Base, metadata
from database.config import DatabaseSettings, get_database_settings
from database.interfaces import IDatabaseManager, ISessionManager, IUnitOfWork
from database.manager import DatabaseManager
from database.models import (
	AlertModel,
	AuthEventModel,
	EnforcementActionModel,
	EventProcessingRunModel,
	EventSourceModel,
	FeatureSnapshotModel,
	HostInteractionSnapshotModel,
	IngestionCredentialModel,
	PolicyDecisionModel,
	ProviderRegistryModel,
	RiskScoreModel,
	TenantHashKeyVersionModel,
	TenantModel,
	TenantOperatingModeModel,
	TenantProviderConnectionModel,
	TenantThresholdProfileModel,
)
from database.session import (
	AsyncDatabaseConfig,
	SessionManager,
	create_database_engine,
	create_session_factory,
	normalize_async_database_url,
)
from database.uow import SqlAlchemyUnitOfWork

__all__ = [
	'AlertModel',
	'AsyncDatabaseConfig',
	'AuthEventModel',
	'Base',
	'DatabaseManager',
	'DatabaseSettings',
	'EnforcementActionModel',
	'EventProcessingRunModel',
	'EventSourceModel',
	'FeatureSnapshotModel',
	'HostInteractionSnapshotModel',
	'IDatabaseManager',
	'ISessionManager',
	'IUnitOfWork',
	'IngestionCredentialModel',
	'PolicyDecisionModel',
	'ProviderRegistryModel',
	'RiskScoreModel',
	'SessionManager',
	'SqlAlchemyUnitOfWork',
	'TenantHashKeyVersionModel',
	'TenantModel',
	'TenantOperatingModeModel',
	'TenantProviderConnectionModel',
	'TenantThresholdProfileModel',
	'create_database_engine',
	'create_session_factory',
	'get_database_settings',
	'metadata',
	'normalize_async_database_url',
]
