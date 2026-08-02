from uuid import UUID

from domain.exceptions import EventSourceNotFoundError
from schemas.tenant import (
	EventSourceCreateSchema,
	EventSourceFilterParams,
	EventSourceUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import EventSourceModel


class EventSourceRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the event source repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_event_source(
		self,
		tenant_id: UUID,
		payload: EventSourceCreateSchema,
	) -> EventSourceModel:
		"""Persist an event source.

		Args:
			tenant_id: The owning tenant identifier.
			payload: The event source creation payload.

		Returns:
			The persisted event source model.
		"""
		event_source = EventSourceModel(tenant_id=tenant_id, **payload.model_dump())
		self._session.add(event_source)
		await self._session.flush()
		await self._session.refresh(event_source)
		return event_source

	async def update_event_source(
		self,
		event_source_id: UUID,
		payload: EventSourceUpdateSchema,
	) -> EventSourceModel:
		"""Persist updates to an event source.

		Args:
			event_source_id: The event source identifier to update.
			payload: The event source update payload.

		Returns:
			The updated event source model.

		Raises:
			EventSourceNotFoundError: If the event source does not exist.
		"""
		event_source = await self.get_event_source_by_id_or_raise(event_source_id)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(event_source, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(event_source)
		return event_source

	async def delete_event_source(self, event_source_id: UUID) -> None:
		"""Delete an event source by identifier.

		Args:
			event_source_id: The event source identifier to delete.

		Raises:
			EventSourceNotFoundError: If the event source does not exist.
		"""
		event_source = await self.get_event_source_by_id_or_raise(event_source_id)
		await self._session.delete(event_source)
		await self._session.flush()

	async def list_event_sources_for_tenant(
		self,
		tenant_id: UUID,
		filters: EventSourceFilterParams,
	) -> list[EventSourceModel]:
		"""Return all event sources for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Event source filter parameters.

		Returns:
			The event source models associated with the tenant.
		"""
		statement = select(EventSourceModel).where(
			EventSourceModel.tenant_id == tenant_id
		)
		if filters.source_type is not None:
			statement = statement.where(
				EventSourceModel.source_type == filters.source_type
			)
		if filters.status is not None:
			statement = statement.where(EventSourceModel.status == filters.status)
		if filters.vendor is not None:
			statement = statement.where(
				EventSourceModel.vendor.ilike(f'%{filters.vendor}%')
			)

		result = await self._session.execute(statement)
		return list(result.scalars().all())

	async def get_event_source_by_id(
		self,
		event_source_id: UUID,
	) -> EventSourceModel | None:
		"""Return an event source by identifier, if present.

		Args:
			event_source_id: The event source identifier to resolve.

		Returns:
			The matching event source model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(EventSourceModel).where(EventSourceModel.id == event_source_id)
		)
		return result.scalar_one_or_none()

	async def get_event_source_by_id_or_raise(
		self,
		event_source_id: UUID,
	) -> EventSourceModel:
		"""Return an event source by identifier or raise if it is missing.

		Args:
			event_source_id: The event source identifier to resolve.

		Returns:
			The matching event source model.

		Raises:
			EventSourceNotFoundError: If the event source does not exist.
		"""
		event_source = await self.get_event_source_by_id(event_source_id)
		if event_source is None:
			raise EventSourceNotFoundError(
				f'Event source "{event_source_id}" does not exist.'
			)

		return event_source
