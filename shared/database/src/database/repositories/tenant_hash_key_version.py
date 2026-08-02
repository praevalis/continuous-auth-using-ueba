from uuid import UUID

from domain.exceptions import TenantHashKeyVersionNotFoundError
from schemas.tenant import (
	TenantHashKeyVersionCreateSchema,
	TenantHashKeyVersionFilterParams,
	TenantHashKeyVersionUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TenantHashKeyVersionModel


class TenantHashKeyVersionRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the tenant hash key version repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_hash_key_version(
		self,
		tenant_id: UUID,
		payload: TenantHashKeyVersionCreateSchema,
	) -> TenantHashKeyVersionModel:
		"""Persist a tenant hash key version.

		Args:
			tenant_id: The owning tenant identifier.
			payload: The hash key version creation payload.

		Returns:
			The persisted hash key version model.
		"""
		hash_key_version = TenantHashKeyVersionModel(
			tenant_id=tenant_id,
			**payload.model_dump(),
			is_active=True,
		)
		self._session.add(hash_key_version)
		await self._session.flush()
		await self._session.refresh(hash_key_version)
		return hash_key_version

	async def update_hash_key_version(
		self,
		hash_key_version_id: UUID,
		payload: TenantHashKeyVersionUpdateSchema,
	) -> TenantHashKeyVersionModel:
		"""Persist updates to a hash key version.

		Args:
			hash_key_version_id: The hash key version identifier to update.
			payload: The hash key version update payload.

		Returns:
			The updated hash key version model.

		Raises:
			TenantHashKeyVersionNotFoundError: If the hash key version does not
				exist.
		"""
		hash_key_version = await self.get_hash_key_version_by_id_or_raise(
			hash_key_version_id=hash_key_version_id
		)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(hash_key_version, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(hash_key_version)
		return hash_key_version

	async def list_hash_key_versions_for_tenant(
		self,
		tenant_id: UUID,
		filters: TenantHashKeyVersionFilterParams,
	) -> list[TenantHashKeyVersionModel]:
		"""Return all hash key versions for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Hash key version filter parameters.

		Returns:
			The hash key version models associated with the tenant.
		"""
		statement = select(TenantHashKeyVersionModel).where(
			TenantHashKeyVersionModel.tenant_id == tenant_id
		)
		if filters.key_version is not None:
			statement = statement.where(
				TenantHashKeyVersionModel.key_version == filters.key_version
			)
		if filters.is_active is not None:
			statement = statement.where(
				TenantHashKeyVersionModel.is_active == filters.is_active
			)

		result = await self._session.execute(statement)
		return list(result.scalars().all())

	async def get_hash_key_version_by_id(
		self,
		hash_key_version_id: UUID,
	) -> TenantHashKeyVersionModel | None:
		"""Return a hash key version by identifier, if present.

		Args:
			hash_key_version_id: The hash key version identifier to resolve.

		Returns:
			The matching hash key version model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(TenantHashKeyVersionModel).where(
				TenantHashKeyVersionModel.id == hash_key_version_id
			)
		)
		return result.scalar_one_or_none()

	async def get_hash_key_version_by_id_or_raise(
		self,
		hash_key_version_id: UUID,
	) -> TenantHashKeyVersionModel:
		"""Return a hash key version by identifier or raise if it is missing.

		Args:
			hash_key_version_id: The hash key version identifier to resolve.

		Returns:
			The matching hash key version model.

		Raises:
			TenantHashKeyVersionNotFoundError: If the hash key version does not
				exist.
		"""
		hash_key_version = await self.get_hash_key_version_by_id(hash_key_version_id)
		if hash_key_version is None:
			raise TenantHashKeyVersionNotFoundError(
				f'Tenant hash key version "{hash_key_version_id}" does not exist.'
			)

		return hash_key_version
