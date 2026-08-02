from uuid import UUID

from domain.exceptions import TenantOperatingModeNotFoundError
from schemas.tenant import (
	TenantOperatingModeCreateSchema,
	TenantOperatingModeFilterParams,
	TenantOperatingModeUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TenantOperatingModeModel


class TenantOperatingModeRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the tenant operating mode repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_operating_mode(
		self,
		tenant_id: UUID,
		payload: TenantOperatingModeCreateSchema,
	) -> TenantOperatingModeModel:
		"""Persist a tenant operating mode record.

		Args:
			tenant_id: The owning tenant identifier.
			payload: The operating mode creation payload.

		Returns:
			The persisted operating mode model.
		"""
		operating_mode = TenantOperatingModeModel(
			tenant_id=tenant_id,
			**payload.model_dump(),
			is_active=True,
		)
		self._session.add(operating_mode)
		await self._session.flush()
		await self._session.refresh(operating_mode)
		return operating_mode

	async def update_operating_mode(
		self,
		operating_mode_id: UUID,
		payload: TenantOperatingModeUpdateSchema,
	) -> TenantOperatingModeModel:
		"""Persist updates to an operating mode record.

		Args:
			operating_mode_id: The operating mode identifier to update.
			payload: The operating mode update payload.

		Returns:
			The updated operating mode model.

		Raises:
			TenantOperatingModeNotFoundError: If the operating mode does not exist.
		"""
		operating_mode = await self.get_operating_mode_by_id_or_raise(
			operating_mode_id=operating_mode_id
		)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(operating_mode, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(operating_mode)
		return operating_mode

	async def list_operating_modes_for_tenant(
		self,
		tenant_id: UUID,
		filters: TenantOperatingModeFilterParams,
	) -> list[TenantOperatingModeModel]:
		"""Return all operating modes for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Operating mode filter parameters.

		Returns:
			The operating mode models associated with the tenant.
		"""
		statement = select(TenantOperatingModeModel).where(
			TenantOperatingModeModel.tenant_id == tenant_id
		)
		if filters.mode is not None:
			statement = statement.where(TenantOperatingModeModel.mode == filters.mode)
		if filters.is_active is not None:
			statement = statement.where(
				TenantOperatingModeModel.is_active == filters.is_active
			)

		result = await self._session.execute(statement)
		return list(result.scalars().all())

	async def get_operating_mode_by_id(
		self,
		operating_mode_id: UUID,
	) -> TenantOperatingModeModel | None:
		"""Return an operating mode by identifier, if present.

		Args:
			operating_mode_id: The operating mode identifier to resolve.

		Returns:
			The matching operating mode model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(TenantOperatingModeModel).where(
				TenantOperatingModeModel.id == operating_mode_id
			)
		)
		return result.scalar_one_or_none()

	async def get_operating_mode_by_id_or_raise(
		self,
		operating_mode_id: UUID,
	) -> TenantOperatingModeModel:
		"""Return an operating mode by identifier or raise if it is missing.

		Args:
			operating_mode_id: The operating mode identifier to resolve.

		Returns:
			The matching operating mode model.

		Raises:
			TenantOperatingModeNotFoundError: If the operating mode does not exist.
		"""
		operating_mode = await self.get_operating_mode_by_id(operating_mode_id)
		if operating_mode is None:
			raise TenantOperatingModeNotFoundError(
				f'Tenant operating mode "{operating_mode_id}" does not exist.'
			)

		return operating_mode
