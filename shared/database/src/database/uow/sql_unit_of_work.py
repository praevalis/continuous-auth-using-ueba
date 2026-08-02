from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import (
	EventSourceRepository,
	IngestionCredentialRepository,
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
		self._tenants = TenantRepository(session)
		self._tenant_operating_modes = TenantOperatingModeRepository(session)
		self._tenant_threshold_profiles = TenantThresholdProfileRepository(session)
		self._tenant_hash_key_versions = TenantHashKeyVersionRepository(session)
		self._event_sources = EventSourceRepository(session)
		self._ingestion_credentials = IngestionCredentialRepository(session)

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
	def ingestion_credentials(self) -> IngestionCredentialRepository:
		"""Return the ingestion credential repository."""
		return self._ingestion_credentials

	async def commit(self) -> None:
		"""Commit the current transaction."""
		await self._session.commit()

	async def rollback(self) -> None:
		"""Rollback the current transaction."""
		await self._session.rollback()

	async def close(self) -> None:
		"""Close the underlying session."""
		await self._session.close()
