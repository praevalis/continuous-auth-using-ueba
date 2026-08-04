from datetime import datetime
from uuid import UUID

from domain.exceptions import TenantThresholdProfileNotFoundError
from schemas.tenant import (
	TenantThresholdProfileCreateSchema,
	TenantThresholdProfileFilterParams,
	TenantThresholdProfileUpdateSchema,
)
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TenantThresholdProfileModel


class TenantThresholdProfileRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the tenant threshold profile repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_threshold_profile(
		self,
		tenant_id: UUID,
		payload: TenantThresholdProfileCreateSchema,
	) -> TenantThresholdProfileModel:
		"""Persist a tenant threshold profile.

		Args:
			tenant_id: The owning tenant identifier.
			payload: The threshold profile creation payload.

		Returns:
			The persisted threshold profile model.
		"""
		threshold_profile = TenantThresholdProfileModel(
			tenant_id=tenant_id,
			**payload.model_dump(),
			is_active=True,
		)
		self._session.add(threshold_profile)
		await self._session.flush()
		await self._session.refresh(threshold_profile)
		return threshold_profile

	async def update_threshold_profile(
		self,
		threshold_profile_id: UUID,
		payload: TenantThresholdProfileUpdateSchema,
	) -> TenantThresholdProfileModel:
		"""Persist updates to a threshold profile.

		Args:
			threshold_profile_id: The threshold profile identifier to update.
			payload: The threshold profile update payload.

		Returns:
			The updated threshold profile model.

		Raises:
			TenantThresholdProfileNotFoundError: If the threshold profile does not
				exist.
		"""
		threshold_profile = await self.get_threshold_profile_by_id_or_raise(
			threshold_profile_id=threshold_profile_id
		)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(threshold_profile, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(threshold_profile)
		return threshold_profile

	async def list_threshold_profiles_for_tenant(
		self,
		tenant_id: UUID,
		filters: TenantThresholdProfileFilterParams,
	) -> list[TenantThresholdProfileModel]:
		"""Return all threshold profiles for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Threshold profile filter parameters.

		Returns:
			The threshold profile models associated with the tenant.
		"""
		statement = select(TenantThresholdProfileModel).where(
			TenantThresholdProfileModel.tenant_id == tenant_id
		)
		if filters.name is not None:
			statement = statement.where(
				TenantThresholdProfileModel.name.ilike(f'%{filters.name}%')
			)
		if filters.is_active is not None:
			statement = statement.where(
				TenantThresholdProfileModel.is_active == filters.is_active
			)

		result = await self._session.execute(statement)
		return list(result.scalars().all())

	async def get_threshold_profile_by_id(
		self,
		threshold_profile_id: UUID,
	) -> TenantThresholdProfileModel | None:
		"""Return a threshold profile by identifier, if present.

		Args:
			threshold_profile_id: The threshold profile identifier to resolve.

		Returns:
			The matching threshold profile model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(TenantThresholdProfileModel).where(
				TenantThresholdProfileModel.id == threshold_profile_id
			)
		)
		return result.scalar_one_or_none()

	async def get_threshold_profile_by_id_or_raise(
		self,
		threshold_profile_id: UUID,
	) -> TenantThresholdProfileModel:
		"""Return a threshold profile by identifier or raise if it is missing.

		Args:
			threshold_profile_id: The threshold profile identifier to resolve.

		Returns:
			The matching threshold profile model.

		Raises:
			TenantThresholdProfileNotFoundError: If the threshold profile does not
				exist.
		"""
		threshold_profile = await self.get_threshold_profile_by_id(threshold_profile_id)
		if threshold_profile is None:
			raise TenantThresholdProfileNotFoundError(
				f'Tenant threshold profile "{threshold_profile_id}" does not exist.'
			)

		return threshold_profile

	async def get_active_threshold_profile_for_tenant(
		self,
		tenant_id: UUID,
		as_of: datetime,
	) -> TenantThresholdProfileModel | None:
		"""Return the active threshold profile for a tenant at a point in time.

		Args:
			tenant_id: The owning tenant identifier.
			as_of: The point in time the profile should be active for.

		Returns:
			The active threshold profile when found, otherwise ``None``.
		"""
		statement = (
			select(TenantThresholdProfileModel)
			.where(
				TenantThresholdProfileModel.tenant_id == tenant_id,
				TenantThresholdProfileModel.is_active.is_(True),
				TenantThresholdProfileModel.effective_from <= as_of,
				or_(
					TenantThresholdProfileModel.effective_to.is_(None),
					TenantThresholdProfileModel.effective_to >= as_of,
				),
			)
			.order_by(TenantThresholdProfileModel.effective_from.desc())
		)
		result = await self._session.execute(statement)
		return result.scalars().first()
