from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import InvalidEventSourceStateError
from domain.tenant import EventSourceStatus
from schemas.tenant import (
	EventSourceCreateSchema,
	EventSourceFilterParams,
	EventSourceMetadataUpdateSchema,
	EventSourceSchema,
	EventSourceUpdateSchema,
)


class EventSourceService:
	def __init__(self, uow: IUnitOfWork) -> None:
		"""Initialize the event source service.

		Args:
			uow: The request-scoped database unit of work.
		"""
		self._uow = uow

	async def create_event_source(
		self,
		tenant_id: UUID,
		payload: EventSourceCreateSchema,
	) -> EventSourceSchema:
		"""Create an event source for a tenant.

		Args:
			tenant_id: The tenant identifier.
			payload: The event source payload.

		Returns:
			The created event source schema.

		Raises:
			TenantNotFoundError: If the tenant does not exist.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)

		event_source_model = await self._uow.event_sources.create_event_source(
			tenant_id,
			payload,
		)
		await self._uow.commit()
		return EventSourceSchema.model_validate(event_source_model)

	async def list_event_sources(
		self,
		tenant_id: UUID,
		filters: EventSourceFilterParams,
	) -> list[EventSourceSchema]:
		"""Return event sources for a tenant.

		Args:
			tenant_id: The tenant identifier.
			filters: The event source filter parameters.

		Returns:
			The event source response schemas for the tenant.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		event_source_models = (
			await self._uow.event_sources.list_event_sources_for_tenant(
				tenant_id,
				filters,
			)
		)
		return [
			EventSourceSchema.model_validate(event_source_model)
			for event_source_model in event_source_models
		]

	async def get_event_source(self, event_source_id: UUID) -> EventSourceSchema:
		"""Return an event source by identifier.

		Args:
			event_source_id: The event source identifier.

		Returns:
			The matching event source response schema.
		"""
		event_source_model = (
			await self._uow.event_sources.get_event_source_by_id_or_raise(
				event_source_id
			)
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			event_source_model.tenant_id
		)
		return EventSourceSchema.model_validate(event_source_model)

	async def update_event_source(
		self,
		event_source_id: UUID,
		payload: EventSourceMetadataUpdateSchema,
	) -> EventSourceSchema:
		"""Update event source metadata by identifier.

		Args:
			event_source_id: The event source identifier.
			payload: The event source metadata update payload.

		Returns:
			The updated event source response schema.
		"""
		event_source_model = (
			await self._uow.event_sources.get_event_source_by_id_or_raise(
				event_source_id
			)
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			event_source_model.tenant_id
		)
		updated_event_source_model = await self._uow.event_sources.update_event_source(
			event_source_id,
			EventSourceUpdateSchema.model_validate(
				payload.model_dump(exclude_unset=True)
			),
		)
		await self._uow.commit()
		return EventSourceSchema.model_validate(updated_event_source_model)

	async def activate_event_source(self, event_source_id: UUID) -> EventSourceSchema:
		"""Activate a disabled event source.

		Args:
			event_source_id: The event source identifier.

		Returns:
			The activated event source response schema.
		"""
		event_source_model = (
			await self._uow.event_sources.get_event_source_by_id_or_raise(
				event_source_id
			)
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			event_source_model.tenant_id
		)
		if event_source_model.status == EventSourceStatus.ACTIVE:
			raise InvalidEventSourceStateError(
				f'Event source "{event_source_id}" is already active.'
			)

		updated_event_source_model = await self._uow.event_sources.update_event_source(
			event_source_id,
			EventSourceUpdateSchema(status=EventSourceStatus.ACTIVE),
		)
		await self._uow.commit()
		return EventSourceSchema.model_validate(updated_event_source_model)

	async def disable_event_source(self, event_source_id: UUID) -> EventSourceSchema:
		"""Disable an active event source.

		Args:
			event_source_id: The event source identifier.

		Returns:
			The disabled event source response schema.
		"""
		event_source_model = (
			await self._uow.event_sources.get_event_source_by_id_or_raise(
				event_source_id
			)
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			event_source_model.tenant_id
		)
		if event_source_model.status == EventSourceStatus.DISABLED:
			raise InvalidEventSourceStateError(
				f'Event source "{event_source_id}" is already disabled.'
			)

		updated_event_source_model = await self._uow.event_sources.update_event_source(
			event_source_id,
			EventSourceUpdateSchema(status=EventSourceStatus.DISABLED),
		)
		await self._uow.commit()
		return EventSourceSchema.model_validate(updated_event_source_model)

	async def delete_event_source(self, event_source_id: UUID) -> None:
		"""Delete an event source by identifier.

		Args:
			event_source_id: The event source identifier.
		"""
		event_source_model = (
			await self._uow.event_sources.get_event_source_by_id_or_raise(
				event_source_id
			)
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			event_source_model.tenant_id
		)
		await self._uow.event_sources.delete_event_source(event_source_id)
		await self._uow.commit()
