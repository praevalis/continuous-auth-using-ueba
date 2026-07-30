"""Shared database package."""

from database.base import Base, metadata
from database.config import DatabaseSettings, get_database_settings
from database.interfaces import ISessionManager
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
	RiskScoreModel,
	TenantHashKeyVersionModel,
	TenantModel,
	TenantOperatingModeModel,
	TenantThresholdProfileModel,
)
from database.session import (
	AsyncDatabaseConfig,
	SessionManager,
	create_database_engine,
	create_session_factory,
	normalize_async_database_url,
)

__all__ = [
	'AlertModel',
	'AsyncDatabaseConfig',
	'AuthEventModel',
	'Base',
	'DatabaseSettings',
	'EnforcementActionModel',
	'EventProcessingRunModel',
	'EventSourceModel',
	'FeatureSnapshotModel',
	'HostInteractionSnapshotModel',
	'IngestionCredentialModel',
	'ISessionManager',
	'PolicyDecisionModel',
	'RiskScoreModel',
	'SessionManager',
	'TenantHashKeyVersionModel',
	'TenantModel',
	'TenantOperatingModeModel',
	'TenantThresholdProfileModel',
	'create_database_engine',
	'create_session_factory',
	'get_database_settings',
	'metadata',
	'normalize_async_database_url',
]
