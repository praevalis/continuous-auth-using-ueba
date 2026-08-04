from sqlalchemy.ext.asyncio import AsyncSession

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


class SqlAlchemyUnitOfWork:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the SQLAlchemy unit of work.

		Args:
			session: The async session backing the unit of work.
		"""
		self._session = session
		self._auth_events = AuthEventRepository(session)
		self._tenants = TenantRepository(session)
		self._tenant_operating_modes = TenantOperatingModeRepository(session)
		self._tenant_threshold_profiles = TenantThresholdProfileRepository(session)
		self._tenant_hash_key_versions = TenantHashKeyVersionRepository(session)
		self._event_sources = EventSourceRepository(session)
		self._event_processing_runs = EventProcessingRunRepository(session)
		self._feature_snapshots = FeatureSnapshotRepository(session)
		self._host_interaction_snapshots = HostInteractionSnapshotRepository(session)
		self._ingestion_credentials = IngestionCredentialRepository(session)
		self._risk_scores = RiskScoreRepository(session)

	@property
	def auth_events(self) -> AuthEventRepository:
		"""Return the auth-event repository."""
		return self._auth_events

	@property
	def tenants(self) -> TenantRepository:
		"""Return the tenant repository."""
		return self._tenants

	@property
	def tenant_operating_modes(self) -> TenantOperatingModeRepository:
		"""Return the tenant operating mode repository."""
		return self._tenant_operating_modes

	@property
	def tenant_threshold_profiles(self) -> TenantThresholdProfileRepository:
		"""Return the tenant threshold profile repository."""
		return self._tenant_threshold_profiles

	@property
	def tenant_hash_key_versions(self) -> TenantHashKeyVersionRepository:
		"""Return the tenant hash key version repository."""
		return self._tenant_hash_key_versions

	@property
	def event_sources(self) -> EventSourceRepository:
		"""Return the event source repository."""
		return self._event_sources

	@property
	def event_processing_runs(self) -> EventProcessingRunRepository:
		"""Return the event processing run repository."""
		return self._event_processing_runs

	@property
	def feature_snapshots(self) -> FeatureSnapshotRepository:
		"""Return the feature snapshot repository."""
		return self._feature_snapshots

	@property
	def host_interaction_snapshots(self) -> HostInteractionSnapshotRepository:
		"""Return the host interaction snapshot repository."""
		return self._host_interaction_snapshots

	@property
	def ingestion_credentials(self) -> IngestionCredentialRepository:
		"""Return the ingestion credential repository."""
		return self._ingestion_credentials

	@property
	def risk_scores(self) -> RiskScoreRepository:
		"""Return the risk score repository."""
		return self._risk_scores

	async def commit(self) -> None:
		"""Commit the current transaction."""
		await self._session.commit()

	async def rollback(self) -> None:
		"""Rollback the current transaction."""
		await self._session.rollback()

	async def close(self) -> None:
		"""Close the underlying session."""
		await self._session.close()
