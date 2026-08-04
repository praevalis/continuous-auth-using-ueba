from uuid import UUID

from domain.exceptions import (
	AuthEventNotFoundError,
	EventProcessingRunNotFoundError,
	TenantNotFoundError,
)
from schemas.scoring import (
	EventProcessingRunCreateSchema,
	EventProcessingRunFilterParams,
	EventProcessingRunUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import EventProcessingRunModel


class EventProcessingRunRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the event processing run repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_event_processing_run(
		self,
		payload: EventProcessingRunCreateSchema,
	) -> EventProcessingRunModel:
		"""Persist an event processing run.

		Args:
			payload: The event processing run creation payload.

		Returns:
			The persisted event processing run model.
		"""
		processing_run = EventProcessingRunModel(**payload.model_dump())
		self._session.add(processing_run)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(
				error, 'fk_event_processing_runs_tenant_id_tenants'
			):
				raise TenantNotFoundError(
					f'Tenant "{payload.tenant_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_event_processing_runs_auth_event_id_auth_events'
			):
				raise AuthEventNotFoundError(
					f'Auth event "{payload.auth_event_id}" does not exist.'
				) from error
			raise

		await self._session.refresh(processing_run)
		return processing_run

	async def get_event_processing_run_by_id(
		self,
		processing_run_id: UUID,
	) -> EventProcessingRunModel | None:
		"""Return an event processing run by identifier, if present.

		Args:
			processing_run_id: The event processing run identifier to resolve.

		Returns:
			The matching event processing run model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(EventProcessingRunModel).where(
				EventProcessingRunModel.id == processing_run_id
			)
		)
		return result.scalar_one_or_none()

	async def get_event_processing_run_by_id_or_raise(
		self,
		processing_run_id: UUID,
	) -> EventProcessingRunModel:
		"""Return an event processing run by identifier or raise if it is missing.

		Args:
			processing_run_id: The event processing run identifier to resolve.

		Returns:
			The matching event processing run model.

		Raises:
			EventProcessingRunNotFoundError: If the event processing run does not
				exist.
		"""
		processing_run = await self.get_event_processing_run_by_id(processing_run_id)
		if processing_run is None:
			raise EventProcessingRunNotFoundError(
				f'Event processing run "{processing_run_id}" does not exist.'
			)

		return processing_run

	async def list_event_processing_runs_for_tenant(
		self,
		tenant_id: UUID,
		filters: EventProcessingRunFilterParams,
	) -> list[EventProcessingRunModel]:
		"""Return event processing runs for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Event processing run filter parameters.

		Returns:
			The event processing run models associated with the tenant.
		"""
		statement = select(EventProcessingRunModel).where(
			EventProcessingRunModel.tenant_id == tenant_id
		)

		if filters.auth_event_id is not None:
			statement = statement.where(
				EventProcessingRunModel.auth_event_id == filters.auth_event_id
			)
		if filters.job_type is not None:
			statement = statement.where(
				EventProcessingRunModel.job_type == filters.job_type
			)
		if filters.status is not None:
			statement = statement.where(
				EventProcessingRunModel.status == filters.status
			)

		result = await self._session.execute(statement)
		return list(result.scalars().all())

	async def update_event_processing_run(
		self,
		processing_run_id: UUID,
		payload: EventProcessingRunUpdateSchema,
	) -> EventProcessingRunModel:
		"""Persist updates to an event processing run.

		Args:
			processing_run_id: The event processing run identifier to update.
			payload: The event processing run update payload.

		Returns:
			The updated event processing run model.

		Raises:
			EventProcessingRunNotFoundError: If the event processing run does not
				exist.
		"""
		processing_run = await self.get_event_processing_run_by_id_or_raise(
			processing_run_id
		)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(processing_run, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(processing_run)
		return processing_run

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
