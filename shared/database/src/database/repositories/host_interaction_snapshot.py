from uuid import UUID

from domain.exceptions import (
	AuthEventNotFoundError,
	EventProcessingRunNotFoundError,
	HostInteractionSnapshotAlreadyExistsError,
	HostInteractionSnapshotNotFoundError,
	TenantNotFoundError,
)
from schemas.scoring import (
	HostInteractionSnapshotCreateSchema,
	HostInteractionSnapshotFilterParams,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import HostInteractionSnapshotModel


class HostInteractionSnapshotRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the host interaction snapshot repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_host_interaction_snapshots(
		self,
		payloads: list[HostInteractionSnapshotCreateSchema],
	) -> list[HostInteractionSnapshotModel]:
		"""Persist computed host interaction snapshots.

		Args:
			payloads: The host interaction snapshot creation payloads.

		Returns:
			The persisted host interaction snapshot models.
		"""
		snapshots = [
			HostInteractionSnapshotModel(**payload.model_dump()) for payload in payloads
		]
		if not snapshots:
			return []

		self._session.add_all(snapshots)

		try:
			await self._session.flush()
		except IntegrityError as error:
			first_payload = payloads[0]

			if self._matches_constraint(
				error, 'uq_host_interaction_snapshots_tenant_id'
			):
				raise HostInteractionSnapshotAlreadyExistsError(
					'Host interaction snapshot already exists for the provided '
					'tenant, auth event, processing run, user, and host.'
				) from error

			if self._matches_constraint(
				error, 'fk_host_interaction_snapshots_tenant_id_tenants'
			):
				raise TenantNotFoundError(
					f'Tenant "{first_payload.tenant_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_host_interaction_snapshots_auth_event_id_auth_events'
			):
				raise AuthEventNotFoundError(
					f'Auth event "{first_payload.auth_event_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error,
				'fk_host_interaction_snapshots_processing_run_id_event_processing_runs',
			):
				raise EventProcessingRunNotFoundError(
					f'Event processing run "{first_payload.processing_run_id}" does not exist.'
				) from error

			raise

		return snapshots

	async def create_host_interaction_snapshot(
		self,
		payload: HostInteractionSnapshotCreateSchema,
	) -> HostInteractionSnapshotModel:
		"""Persist a computed host interaction snapshot.

		Args:
			payload: The host interaction snapshot creation payload.

		Returns:
			The persisted host interaction snapshot model.
		"""
		snapshots = await self.create_host_interaction_snapshots([payload])
		return snapshots[0]

	async def get_host_interaction_snapshot_by_id(
		self,
		host_interaction_snapshot_id: UUID,
	) -> HostInteractionSnapshotModel | None:
		"""Return a host interaction snapshot by identifier, if present.

		Args:
			host_interaction_snapshot_id: The host interaction snapshot identifier to
				resolve.

		Returns:
			The matching host interaction snapshot model when found, otherwise
			``None``.
		"""
		result = await self._session.execute(
			select(HostInteractionSnapshotModel).where(
				HostInteractionSnapshotModel.id == host_interaction_snapshot_id
			)
		)
		return result.scalar_one_or_none()

	async def get_host_interaction_snapshot_by_id_or_raise(
		self,
		host_interaction_snapshot_id: UUID,
	) -> HostInteractionSnapshotModel:
		"""Return a host interaction snapshot by identifier or raise if missing.

		Args:
			host_interaction_snapshot_id: The host interaction snapshot identifier to
				resolve.

		Returns:
			The matching host interaction snapshot model.

		Raises:
			HostInteractionSnapshotNotFoundError: If the host interaction snapshot
				does not exist.
		"""
		host_interaction_snapshot = await self.get_host_interaction_snapshot_by_id(
			host_interaction_snapshot_id
		)
		if host_interaction_snapshot is None:
			raise HostInteractionSnapshotNotFoundError(
				f'Host interaction snapshot "{host_interaction_snapshot_id}" does not exist.'
			)

		return host_interaction_snapshot

	async def list_host_interaction_snapshots_for_tenant(
		self,
		tenant_id: UUID,
		filters: HostInteractionSnapshotFilterParams,
	) -> list[HostInteractionSnapshotModel]:
		"""Return host interaction snapshots for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Host interaction snapshot filter parameters.

		Returns:
			The host interaction snapshot models associated with the tenant.
		"""
		statement = select(HostInteractionSnapshotModel).where(
			HostInteractionSnapshotModel.tenant_id == tenant_id
		)
		if filters.auth_event_id is not None:
			statement = statement.where(
				HostInteractionSnapshotModel.auth_event_id == filters.auth_event_id
			)
		if filters.processing_run_id is not None:
			statement = statement.where(
				HostInteractionSnapshotModel.processing_run_id
				== filters.processing_run_id
			)
		if filters.user_hash is not None:
			statement = statement.where(
				HostInteractionSnapshotModel.user_hash == filters.user_hash
			)
		if filters.host_hash is not None:
			statement = statement.where(
				HostInteractionSnapshotModel.host_hash == filters.host_hash
			)
		if filters.snapshot_version is not None:
			statement = statement.where(
				HostInteractionSnapshotModel.snapshot_version
				== filters.snapshot_version
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
