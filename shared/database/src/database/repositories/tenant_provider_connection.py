from uuid import UUID

from domain.exceptions import (
	ProviderRegistryNotFoundError,
	TenantNotFoundError,
	TenantProviderConnectionAlreadyExistsError,
	TenantProviderConnectionNotFoundError,
)
from schemas.integration import (
	TenantProviderConnectionCreateSchema,
	TenantProviderConnectionFilterParams,
	TenantProviderConnectionUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TenantProviderConnectionModel


class TenantProviderConnectionRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the tenant provider connection repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_tenant_provider_connection(
		self,
		tenant_id: UUID,
		payload: TenantProviderConnectionCreateSchema,
	) -> TenantProviderConnectionModel:
		"""Persist a tenant provider connection.

		Args:
			tenant_id: The owning tenant identifier.
			payload: The tenant provider connection creation payload.

		Returns:
			The persisted tenant provider connection model.

		Raises:
			ProviderRegistryNotFoundError: If the referenced provider registry entry
				does not exist.
			TenantNotFoundError: If the tenant does not exist.
			TenantProviderConnectionAlreadyExistsError: If the tenant already has a
				connection with the same name.
		"""
		tenant_provider_connection = TenantProviderConnectionModel(
			tenant_id=tenant_id,
			**payload.model_dump(),
		)
		self._session.add(tenant_provider_connection)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(
				error,
				'uq_tenant_provider_connections_tenant_id',
			):
				raise TenantProviderConnectionAlreadyExistsError(
					f'Tenant provider connection "{payload.connection_name}" already '
					f'exists for tenant "{tenant_id}".'
				) from error

			if self._matches_constraint(
				error,
				'fk_tenant_provider_connections_tenant_id_tenants',
			):
				raise TenantNotFoundError(
					f'Tenant "{tenant_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error,
				'fk_tenant_provider_connections_provider_registry_id_provider_registry',
			):
				raise ProviderRegistryNotFoundError(
					f'Provider registry entry "{payload.provider_registry_id}" does '
					f'not exist.'
				) from error

			raise

		await self._session.refresh(tenant_provider_connection)
		return tenant_provider_connection

	async def update_tenant_provider_connection(
		self,
		tenant_provider_connection_id: UUID,
		payload: TenantProviderConnectionUpdateSchema,
	) -> TenantProviderConnectionModel:
		"""Persist updates to a tenant provider connection.

		Args:
			tenant_provider_connection_id: The tenant provider connection identifier
				to update.
			payload: The tenant provider connection update payload.

		Returns:
			The updated tenant provider connection model.

		Raises:
			TenantProviderConnectionNotFoundError: If the tenant provider connection
				does not exist.
		"""
		tenant_provider_connection = (
			await self.get_tenant_provider_connection_by_id_or_raise(
				tenant_provider_connection_id
			)
		)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(tenant_provider_connection, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(tenant_provider_connection)
		return tenant_provider_connection

	async def get_tenant_provider_connection_by_id(
		self,
		tenant_provider_connection_id: UUID,
	) -> TenantProviderConnectionModel | None:
		"""Return a tenant provider connection by identifier, if present.

		Args:
			tenant_provider_connection_id: The tenant provider connection identifier
				to resolve.

		Returns:
			The matching tenant provider connection model when found, otherwise
			``None``.
		"""
		result = await self._session.execute(
			select(TenantProviderConnectionModel).where(
				TenantProviderConnectionModel.id == tenant_provider_connection_id
			)
		)
		return result.scalar_one_or_none()

	async def get_tenant_provider_connection_by_id_or_raise(
		self,
		tenant_provider_connection_id: UUID,
	) -> TenantProviderConnectionModel:
		"""Return a tenant provider connection by identifier or raise if missing.

		Args:
			tenant_provider_connection_id: The tenant provider connection identifier
				to resolve.

		Returns:
			The matching tenant provider connection model.

		Raises:
			TenantProviderConnectionNotFoundError: If the tenant provider connection
				does not exist.
		"""
		tenant_provider_connection = await self.get_tenant_provider_connection_by_id(
			tenant_provider_connection_id
		)
		if tenant_provider_connection is None:
			raise TenantProviderConnectionNotFoundError(
				'Tenant provider connection '
				f'"{tenant_provider_connection_id}" does not exist.'
			)

		return tenant_provider_connection

	async def list_tenant_provider_connections_for_tenant(
		self,
		tenant_id: UUID,
		filters: TenantProviderConnectionFilterParams,
	) -> list[TenantProviderConnectionModel]:
		"""Return all tenant provider connections for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Tenant provider connection filter parameters.

		Returns:
			The tenant provider connection models associated with the tenant.
		"""
		statement = select(TenantProviderConnectionModel).where(
			TenantProviderConnectionModel.tenant_id == tenant_id
		)

		if filters.provider_registry_id is not None:
			statement = statement.where(
				TenantProviderConnectionModel.provider_registry_id
				== filters.provider_registry_id
			)

		if filters.status is not None:
			statement = statement.where(
				TenantProviderConnectionModel.status == filters.status
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
