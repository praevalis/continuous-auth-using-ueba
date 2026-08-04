from uuid import UUID

from domain.exceptions import (
	AuthEventNotFoundError,
	EventProcessingRunNotFoundError,
	FeatureSnapshotNotFoundError,
	TenantNotFoundError,
)
from schemas.scoring import FeatureSnapshotCreateSchema, FeatureSnapshotFilterParams
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import FeatureSnapshotModel


class FeatureSnapshotRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the feature snapshot repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_feature_snapshot(
		self,
		payload: FeatureSnapshotCreateSchema,
	) -> FeatureSnapshotModel:
		"""Persist a computed feature snapshot.

		Args:
			payload: The feature snapshot creation payload.

		Returns:
			The persisted feature snapshot model.
		"""
		feature_snapshot = FeatureSnapshotModel(**payload.model_dump())
		self._session.add(feature_snapshot)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(
				error, 'fk_feature_snapshots_tenant_id_tenants'
			):
				raise TenantNotFoundError(
					f'Tenant "{payload.tenant_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_feature_snapshots_auth_event_id_auth_events'
			):
				raise AuthEventNotFoundError(
					f'Auth event "{payload.auth_event_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error,
				'fk_feature_snapshots_processing_run_id_event_processing_runs',
			):
				raise EventProcessingRunNotFoundError(
					f'Event processing run "{payload.processing_run_id}" does not exist.'
				) from error
			raise

		await self._session.refresh(feature_snapshot)
		return feature_snapshot

	async def get_feature_snapshot_by_id(
		self,
		feature_snapshot_id: UUID,
	) -> FeatureSnapshotModel | None:
		"""Return a feature snapshot by identifier, if present.

		Args:
			feature_snapshot_id: The feature snapshot identifier to resolve.

		Returns:
			The matching feature snapshot model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(FeatureSnapshotModel).where(
				FeatureSnapshotModel.id == feature_snapshot_id
			)
		)
		return result.scalar_one_or_none()

	async def get_feature_snapshot_by_id_or_raise(
		self,
		feature_snapshot_id: UUID,
	) -> FeatureSnapshotModel:
		"""Return a feature snapshot by identifier or raise if it is missing.

		Args:
			feature_snapshot_id: The feature snapshot identifier to resolve.

		Returns:
			The matching feature snapshot model.

		Raises:
			FeatureSnapshotNotFoundError: If the feature snapshot does not exist.
		"""
		feature_snapshot = await self.get_feature_snapshot_by_id(feature_snapshot_id)
		if feature_snapshot is None:
			raise FeatureSnapshotNotFoundError(
				f'Feature snapshot "{feature_snapshot_id}" does not exist.'
			)

		return feature_snapshot

	async def list_feature_snapshots_for_tenant(
		self,
		tenant_id: UUID,
		filters: FeatureSnapshotFilterParams,
	) -> list[FeatureSnapshotModel]:
		"""Return feature snapshots for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Feature snapshot filter parameters.

		Returns:
			The feature snapshot models associated with the tenant.
		"""
		statement = select(FeatureSnapshotModel).where(
			FeatureSnapshotModel.tenant_id == tenant_id
		)

		if filters.auth_event_id is not None:
			statement = statement.where(
				FeatureSnapshotModel.auth_event_id == filters.auth_event_id
			)
		if filters.processing_run_id is not None:
			statement = statement.where(
				FeatureSnapshotModel.processing_run_id == filters.processing_run_id
			)
		if filters.feature_version is not None:
			statement = statement.where(
				FeatureSnapshotModel.feature_version == filters.feature_version
			)

		result = await self._session.execute(statement)
		return list(result.scalars().all())

	@staticmethod
	def _matches_constraint(error: IntegrityError, *constraint_names: str) -> bool:
		"""Return whether an integrity error references one of the given constraints.

		Args:
			error: The raised SQLAlchemy integrity error.
			*constraint_names: Known database constraint names to match.

		Returns:
			True when the error references one of the provided constraint names.
		"""
		error_message = str(error.orig)
		return any(
			constraint_name in error_message for constraint_name in constraint_names
		)
