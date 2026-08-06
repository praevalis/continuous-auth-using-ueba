from datetime import UTC, datetime
from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import (
	ActiveProviderRegistryError,
	InactiveProviderRegistryError,
)
from schemas.integration import (
	ProviderRegistryCreateSchema,
	ProviderRegistryFilterParams,
	ProviderRegistrySchema,
	ProviderRegistryUpdateSchema,
)


class ProviderRegistryService:
	def __init__(self, uow: IUnitOfWork) -> None:
		"""Initialize the provider registry service.

		Args:
			uow: The request-scoped database unit of work.
		"""
		self._uow = uow

	async def create_provider_registry(
		self,
		payload: ProviderRegistryCreateSchema,
	) -> ProviderRegistrySchema:
		"""Create a provider registry entry.

		Args:
			payload: The provider registry creation payload.

		Returns:
			The created provider registry response schema.
		"""
		provider_registry_model = (
			await self._uow.provider_registry.create_provider_registry(payload)
		)
		await self._uow.commit()
		return ProviderRegistrySchema.model_validate(provider_registry_model)

	async def list_provider_registry_entries(
		self,
		filters: ProviderRegistryFilterParams,
	) -> list[ProviderRegistrySchema]:
		"""Return provider registry entries matching the provided filters.

		Args:
			filters: The provider registry filter parameters.

		Returns:
			The matching provider registry response schemas.
		"""
		provider_registry_models = (
			await self._uow.provider_registry.list_provider_registry_entries(filters)
		)
		return [
			ProviderRegistrySchema.model_validate(provider_registry_model)
			for provider_registry_model in provider_registry_models
		]

	async def get_provider_registry(
		self,
		provider_registry_id: UUID,
	) -> ProviderRegistrySchema:
		"""Return a provider registry entry by identifier.

		Args:
			provider_registry_id: The provider registry identifier.

		Returns:
			The matching provider registry response schema.
		"""
		provider_registry_model = (
			await self._uow.provider_registry.get_provider_registry_by_id_or_raise(
				provider_registry_id
			)
		)
		return ProviderRegistrySchema.model_validate(provider_registry_model)

	async def update_provider_registry(
		self,
		provider_registry_id: UUID,
		payload: ProviderRegistryUpdateSchema,
	) -> ProviderRegistrySchema:
		"""Update a provider registry entry by identifier.

		Args:
			provider_registry_id: The provider registry identifier.
			payload: The provider registry update payload.

		Returns:
			The updated provider registry response schema.
		"""
		provider_registry_model = (
			await self._uow.provider_registry.update_provider_registry(
				provider_registry_id,
				payload,
			)
		)
		await self._uow.commit()
		return ProviderRegistrySchema.model_validate(provider_registry_model)

	async def deprecate_provider_registry(
		self,
		provider_registry_id: UUID,
	) -> ProviderRegistrySchema:
		"""Deprecate an active provider registry entry.

		Args:
			provider_registry_id: The provider registry identifier.

		Returns:
			The deprecated provider registry response schema.

		Raises:
			InactiveProviderRegistryError: If the provider registry entry is already
				inactive.
		"""
		provider_registry_model = (
			await self._uow.provider_registry.get_provider_registry_by_id_or_raise(
				provider_registry_id
			)
		)
		if not provider_registry_model.is_active:
			raise InactiveProviderRegistryError(
				f'Provider registry entry "{provider_registry_id}" is already inactive.'
			)

		updated_provider_registry_model = (
			await self._uow.provider_registry.update_provider_registry(
				provider_registry_id,
				ProviderRegistryUpdateSchema(
					is_active=False,
					deprecated_at=datetime.now(UTC),
				),
			)
		)
		await self._uow.commit()
		return ProviderRegistrySchema.model_validate(updated_provider_registry_model)

	async def reactivate_provider_registry(
		self,
		provider_registry_id: UUID,
	) -> ProviderRegistrySchema:
		"""Reactivate a deprecated provider registry entry.

		Args:
			provider_registry_id: The provider registry identifier.

		Returns:
			The reactivated provider registry response schema.

		Raises:
			ActiveProviderRegistryError: If the provider registry entry is already
				active.
		"""
		provider_registry_model = (
			await self._uow.provider_registry.get_provider_registry_by_id_or_raise(
				provider_registry_id
			)
		)
		if provider_registry_model.is_active:
			raise ActiveProviderRegistryError(
				f'Provider registry entry "{provider_registry_id}" is already active.'
			)

		updated_provider_registry_model = (
			await self._uow.provider_registry.update_provider_registry(
				provider_registry_id,
				ProviderRegistryUpdateSchema(
					is_active=True,
					deprecated_at=None,
				),
			)
		)
		await self._uow.commit()
		return ProviderRegistrySchema.model_validate(updated_provider_registry_model)
