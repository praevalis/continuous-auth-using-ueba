from datetime import UTC, datetime
from uuid import UUID

from domain.exceptions import TenantAlreadyExistsError, TenantNotFoundError
from domain.tenant import TenantStatus
from schemas.tenant import TenantCreateSchema, TenantFilterParams, TenantUpdateSchema
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TenantModel


class TenantRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the tenant repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_tenant(
		self,
		payload: TenantCreateSchema,
		*,
		slug: str,
	) -> TenantModel:
		"""Persist a tenant from the provided create schema.

		Args:
			payload: The tenant creation payload.
			slug: The generated immutable tenant slug.

		Returns:
			The persisted tenant model.
		"""
		tenant = TenantModel(
			**payload.model_dump(),
			slug=slug,
			status=TenantStatus.ACTIVE,
		)
		self._session.add(tenant)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(error, 'uq_tenants_slug', 'tenants_slug_key'):
				raise TenantAlreadyExistsError(
					f'Tenant with slug "{slug}" already exists.'
				) from error
			raise

		await self._session.refresh(tenant)
		return tenant

	async def update_tenant(
		self,
		tenant_id: UUID,
		payload: TenantUpdateSchema,
	) -> TenantModel:
		"""Persist updates to a tenant model.

		Args:
			tenant_id: The tenant identifier to update.
			payload: The tenant update payload.

		Returns:
			The updated tenant model.

		Raises:
			TenantNotFoundError: If the tenant does not exist.
		"""
		tenant = await self.get_active_tenant_by_id_or_raise(tenant_id)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(tenant, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(tenant)
		return tenant

	async def delete_tenant(self, tenant_id: UUID) -> TenantModel:
		"""Soft delete a tenant.

		Args:
			tenant_id: The tenant identifier to soft delete.

		Returns:
			The soft-deleted tenant model.

		Raises:
			TenantNotFoundError: If the tenant does not exist.
		"""
		tenant = await self.get_active_tenant_by_id_or_raise(tenant_id)
		tenant.deleted_at = datetime.now(UTC)

		await self._session.flush()
		await self._session.refresh(tenant)
		return tenant

	async def get_tenant_by_slug(self, slug: str) -> TenantModel | None:
		"""Return a tenant by slug, if present.

		Args:
			slug: The tenant slug to resolve.

		Returns:
			The matching tenant model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(TenantModel).where(TenantModel.slug == slug)
		)
		return result.scalar_one_or_none()

	async def get_tenant_by_id(self, tenant_id: UUID) -> TenantModel | None:
		"""Return a tenant by identifier, if present.

		Args:
			tenant_id: The tenant identifier to resolve.

		Returns:
			The matching tenant model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(TenantModel).where(TenantModel.id == tenant_id)
		)
		return result.scalar_one_or_none()

	async def list_tenants(
		self,
		filters: TenantFilterParams,
	) -> list[TenantModel]:
		"""Return tenants matching the provided filters.

		Args:
			filters: Tenant filter parameters.

		Returns:
			The tenant models matching the provided filters.
		"""
		statement = select(TenantModel)
		if filters.slug is not None:
			statement = statement.where(TenantModel.slug.ilike(f'%{filters.slug}%'))
		if filters.display_name is not None:
			statement = statement.where(
				TenantModel.display_name.ilike(f'%{filters.display_name}%')
			)
		if filters.status is not None:
			statement = statement.where(TenantModel.status == filters.status)
		if not filters.include_deleted:
			statement = statement.where(TenantModel.deleted_at.is_(None))

		result = await self._session.execute(statement)
		return list(result.scalars().all())

	async def get_active_tenant_by_id_or_raise(self, tenant_id: UUID) -> TenantModel:
		"""Return an active tenant by identifier.

		Args:
			tenant_id: The tenant identifier to resolve.

		Returns:
			The resolved active tenant model.

		Raises:
			TenantNotFoundError: If the tenant does not exist or is soft deleted.
		"""
		tenant = await self.get_tenant_by_id(tenant_id)
		if tenant is None or tenant.deleted_at is not None:
			raise TenantNotFoundError(f'Tenant "{tenant_id}" does not exist.')

		return tenant

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
