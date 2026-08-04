from typing import Protocol

from database.repositories import (
	AuthEventRepository,
	EventProcessingRunRepository,
	EventSourceRepository,
	FeatureSnapshotRepository,
	HostInteractionSnapshotRepository,
	IngestionCredentialRepository,
	RiskScoreRepository,
	TenantHashKeyVersionRepository,
	TenantOperatingModeRepository,
	TenantRepository,
	TenantThresholdProfileRepository,
)


class IUnitOfWork(Protocol):
	@property
	def auth_events(self) -> AuthEventRepository:
		"""Return the auth-event repository."""
		...

	@property
	def tenants(self) -> TenantRepository:
		"""Return the tenant repository."""
		...

	@property
	def tenant_operating_modes(self) -> TenantOperatingModeRepository:
		"""Return the tenant operating mode repository."""
		...

	@property
	def tenant_threshold_profiles(self) -> TenantThresholdProfileRepository:
		"""Return the tenant threshold profile repository."""
		...

	@property
	def tenant_hash_key_versions(self) -> TenantHashKeyVersionRepository:
		"""Return the tenant hash key version repository."""
		...

	@property
	def event_sources(self) -> EventSourceRepository:
		"""Return the event source repository."""
		...

	@property
	def event_processing_runs(self) -> EventProcessingRunRepository:
		"""Return the event processing run repository."""
		...

	@property
	def feature_snapshots(self) -> FeatureSnapshotRepository:
		"""Return the feature snapshot repository."""
		...

	@property
	def host_interaction_snapshots(self) -> HostInteractionSnapshotRepository:
		"""Return the host interaction snapshot repository."""
		...

	@property
	def ingestion_credentials(self) -> IngestionCredentialRepository:
		"""Return the ingestion credential repository."""
		...

	@property
	def risk_scores(self) -> RiskScoreRepository:
		"""Return the risk score repository."""
		...

	async def commit(self) -> None:
		"""Commit the current unit of work transaction."""
		...

	async def rollback(self) -> None:
		"""Rollback the current unit of work transaction."""
		...

	async def close(self) -> None:
		"""Release the underlying unit of work resources."""
		...
