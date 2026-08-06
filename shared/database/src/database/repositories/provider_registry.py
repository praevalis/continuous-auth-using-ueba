from uuid import UUID

from domain.exceptions import (
	ProviderRegistryAlreadyExistsError,
	ProviderRegistryNotFoundError,
)
from schemas.integration import (
	ProviderRegistryCreateSchema,
	ProviderRegistryFilterParams,
	ProviderRegistryUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ProviderRegistryModel


class ProviderRegistryRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the provider registry repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_provider_registry(
		self,
		payload: ProviderRegistryCreateSchema,
	) -> ProviderRegistryModel:
		"""Persist a provider registry entry.

		Args:
			payload: The provider registry creation payload.

		Returns:
			The persisted provider registry model.

		Raises:
			ProviderRegistryAlreadyExistsError: If a provider with the same key
				already exists.
		"""
		provider_registry = ProviderRegistryModel(**payload.model_dump())
		self._session.add(provider_registry)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(
				error,
				'uq_provider_registry_provider_key',
				'provider_registry_provider_key_key',
			):
				raise ProviderRegistryAlreadyExistsError(
					f'Provider registry entry with key "{payload.provider_key}" '
					f'already exists.'
				) from error

			raise

		await self._session.refresh(provider_registry)
		return provider_registry

	async def update_provider_registry(
		self,
		provider_registry_id: UUID,
		payload: ProviderRegistryUpdateSchema,
	) -> ProviderRegistryModel:
		"""Persist updates to a provider registry entry.

		Args:
			provider_registry_id: The provider registry identifier to update.
			payload: The provider registry update payload.

		Returns:
			The updated provider registry model.

		Raises:
			ProviderRegistryNotFoundError: If the provider registry entry does not
				exist.
		"""
		provider_registry = await self.get_provider_registry_by_id_or_raise(
			provider_registry_id
		)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(provider_registry, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(provider_registry)
		return provider_registry

	async def get_provider_registry_by_id(
		self,
		provider_registry_id: UUID,
	) -> ProviderRegistryModel | None:
		"""Return a provider registry entry by identifier, if present.

		Args:
			provider_registry_id: The provider registry identifier to resolve.

		Returns:
			The matching provider registry model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(ProviderRegistryModel).where(
				ProviderRegistryModel.id == provider_registry_id
			)
		)
		return result.scalar_one_or_none()

	async def get_provider_registry_by_id_or_raise(
		self,
		provider_registry_id: UUID,
	) -> ProviderRegistryModel:
		"""Return a provider registry entry by identifier or raise if missing.

		Args:
			provider_registry_id: The provider registry identifier to resolve.

		Returns:
			The matching provider registry model.

		Raises:
			ProviderRegistryNotFoundError: If the provider registry entry does not
				exist.
		"""
		provider_registry = await self.get_provider_registry_by_id(provider_registry_id)
		if provider_registry is None:
			raise ProviderRegistryNotFoundError(
				f'Provider registry entry "{provider_registry_id}" does not exist.'
			)

		return provider_registry

	async def list_provider_registry_entries(
		self,
		filters: ProviderRegistryFilterParams,
	) -> list[ProviderRegistryModel]:
		"""Return provider registry entries matching the provided filters.

		Args:
			filters: Provider registry filter parameters.

		Returns:
			The provider registry models matching the provided filters.
		"""
		statement = select(ProviderRegistryModel)

		if filters.provider_type is not None:
			statement = statement.where(
				ProviderRegistryModel.provider_type == filters.provider_type
			)

		if filters.connection_method is not None:
			statement = statement.where(
				ProviderRegistryModel.connection_method == filters.connection_method
			)

		if filters.is_active is not None:
			statement = statement.where(
				ProviderRegistryModel.is_active == filters.is_active
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
