"""Database repositories package."""

from database.repositories.auth_event import AuthEventRepository
from database.repositories.event_processing_run import EventProcessingRunRepository
from database.repositories.event_source import EventSourceRepository
from database.repositories.feature_snapshot import FeatureSnapshotRepository
from database.repositories.host_interaction_snapshot import (
	HostInteractionSnapshotRepository,
)
from database.repositories.ingestion_credential import IngestionCredentialRepository
from database.repositories.risk_score import RiskScoreRepository
from database.repositories.tenant import TenantRepository
from database.repositories.tenant_hash_key_version import (
	TenantHashKeyVersionRepository,
)
from database.repositories.tenant_operating_mode import (
	TenantOperatingModeRepository,
)
from database.repositories.tenant_threshold_profile import (
	TenantThresholdProfileRepository,
)

__all__ = [
	'AuthEventRepository',
	'EventProcessingRunRepository',
	'EventSourceRepository',
	'FeatureSnapshotRepository',
	'HostInteractionSnapshotRepository',
	'IngestionCredentialRepository',
	'RiskScoreRepository',
	'TenantHashKeyVersionRepository',
	'TenantOperatingModeRepository',
	'TenantRepository',
	'TenantThresholdProfileRepository',
]
