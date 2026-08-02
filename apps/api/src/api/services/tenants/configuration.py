from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import (
	InvalidConfigurationLifecycleError,
	TenantHashKeyVersionNotFoundError,
	TenantOperatingModeNotFoundError,
	TenantThresholdProfileNotFoundError,
)
from domain.tenant import (
	TenantHashKeyVersion,
	TenantOperatingModeRecord,
	TenantThresholdProfile,
)
from domain.tenant.rules import DefaultTenantConfigurationValidator
from schemas.tenant import (
	TenantHashKeyVersionCreateSchema,
	TenantHashKeyVersionFilterParams,
	TenantHashKeyVersionRetireSchema,
	TenantHashKeyVersionSchema,
	TenantHashKeyVersionUpdateSchema,
	TenantOperatingModeCreateSchema,
	TenantOperatingModeFilterParams,
	TenantOperatingModeRetireSchema,
	TenantOperatingModeSchema,
	TenantOperatingModeUpdateSchema,
	TenantThresholdProfileCreateSchema,
	TenantThresholdProfileFilterParams,
	TenantThresholdProfileRetireSchema,
	TenantThresholdProfileSchema,
	TenantThresholdProfileUpdateSchema,
)


class TenantConfigurationService:
	def __init__(self, uow: IUnitOfWork) -> None:
		"""Initialize the tenant configuration service.

		Args:
			uow: The request-scoped database unit of work.
		"""
		self._uow = uow
		self._validator = DefaultTenantConfigurationValidator()

	async def create_operating_mode(
		self,
		tenant_id: UUID,
		payload: TenantOperatingModeCreateSchema,
	) -> TenantOperatingModeSchema:
		"""Create the next active operating mode for a tenant.

		Args:
			tenant_id: The tenant identifier.
			payload: The operating mode creation payload.

		Returns:
			The created operating mode response schema.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		await self._rollover_operating_mode(
			tenant_id=tenant_id,
			effective_from=payload.effective_from,
		)
		operating_mode_model = (
			await self._uow.tenant_operating_modes.create_operating_mode(
				tenant_id, payload
			)
		)
		await self._validate_operating_modes(tenant_id)
		await self._uow.commit()
		return TenantOperatingModeSchema.model_validate(operating_mode_model)

	async def list_operating_modes(
		self,
		tenant_id: UUID,
		filters: TenantOperatingModeFilterParams,
	) -> list[TenantOperatingModeSchema]:
		"""Return operating modes for a tenant.

		Args:
			tenant_id: The tenant identifier.
			filters: The operating mode filter parameters.

		Returns:
			The operating mode response schemas for the tenant.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		operating_mode_models = (
			await self._uow.tenant_operating_modes.list_operating_modes_for_tenant(
				tenant_id,
				filters,
			)
		)
		return [
			TenantOperatingModeSchema.model_validate(operating_mode_model)
			for operating_mode_model in operating_mode_models
		]

	async def get_operating_mode(
		self,
		tenant_id: UUID,
		operating_mode_id: UUID,
	) -> TenantOperatingModeSchema:
		"""Return an operating mode for a tenant.

		Args:
			tenant_id: The tenant identifier.
			operating_mode_id: The operating mode identifier.

		Returns:
			The matching operating mode response schema.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		operating_mode_model = await self._get_tenant_operating_mode(
			tenant_id,
			operating_mode_id,
		)
		return TenantOperatingModeSchema.model_validate(operating_mode_model)

	async def retire_operating_mode(
		self,
		tenant_id: UUID,
		operating_mode_id: UUID,
		payload: TenantOperatingModeRetireSchema,
	) -> TenantOperatingModeSchema:
		"""Retire an active operating mode for a tenant.

		Args:
			tenant_id: The tenant identifier.
			operating_mode_id: The operating mode identifier.
			payload: The operating mode retirement payload.

		Returns:
			The retired operating mode response schema.
		"""
		operating_mode_model = await self._get_tenant_operating_mode(
			tenant_id,
			operating_mode_id,
		)
		effective_to = payload.effective_to or datetime.now(UTC)
		self._validate_retirement_window(
			effective_from=operating_mode_model.effective_from,
			effective_to=effective_to,
			label='operating mode',
		)
		if not operating_mode_model.is_active:
			raise InvalidConfigurationLifecycleError(
				f'Tenant operating mode "{operating_mode_id}" is already inactive.'
			)

		updated_operating_mode_model = (
			await self._uow.tenant_operating_modes.update_operating_mode(
				operating_mode_id,
				TenantOperatingModeUpdateSchema(
					is_active=False,
					effective_to=effective_to,
					changed_by=payload.changed_by,
					change_reason=payload.change_reason,
				),
			)
		)
		await self._validate_operating_modes(tenant_id)
		await self._uow.commit()
		return TenantOperatingModeSchema.model_validate(updated_operating_mode_model)

	async def create_threshold_profile(
		self,
		tenant_id: UUID,
		payload: TenantThresholdProfileCreateSchema,
	) -> TenantThresholdProfileSchema:
		"""Create the next active threshold profile for a tenant.

		Args:
			tenant_id: The tenant identifier.
			payload: The threshold profile creation payload.

		Returns:
			The created threshold profile response schema.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		await self._rollover_threshold_profile(
			tenant_id=tenant_id,
			effective_from=payload.effective_from,
		)
		threshold_profile_model = (
			await self._uow.tenant_threshold_profiles.create_threshold_profile(
				tenant_id,
				payload,
			)
		)
		await self._validate_threshold_profiles(tenant_id)
		await self._uow.commit()
		return TenantThresholdProfileSchema.model_validate(threshold_profile_model)

	async def list_threshold_profiles(
		self,
		tenant_id: UUID,
		filters: TenantThresholdProfileFilterParams,
	) -> list[TenantThresholdProfileSchema]:
		"""Return threshold profiles for a tenant.

		Args:
			tenant_id: The tenant identifier.
			filters: The threshold profile filter parameters.

		Returns:
			The threshold profile response schemas for the tenant.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		threshold_profile_models = await self._uow.tenant_threshold_profiles.list_threshold_profiles_for_tenant(
			tenant_id,
			filters,
		)
		return [
			TenantThresholdProfileSchema.model_validate(threshold_profile_model)
			for threshold_profile_model in threshold_profile_models
		]

	async def get_threshold_profile(
		self,
		tenant_id: UUID,
		threshold_profile_id: UUID,
	) -> TenantThresholdProfileSchema:
		"""Return a threshold profile for a tenant.

		Args:
			tenant_id: The tenant identifier.
			threshold_profile_id: The threshold profile identifier.

		Returns:
			The matching threshold profile response schema.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		threshold_profile_model = await self._get_tenant_threshold_profile(
			tenant_id,
			threshold_profile_id,
		)
		return TenantThresholdProfileSchema.model_validate(threshold_profile_model)

	async def retire_threshold_profile(
		self,
		tenant_id: UUID,
		threshold_profile_id: UUID,
		payload: TenantThresholdProfileRetireSchema,
	) -> TenantThresholdProfileSchema:
		"""Retire an active threshold profile for a tenant.

		Args:
			tenant_id: The tenant identifier.
			threshold_profile_id: The threshold profile identifier.
			payload: The threshold profile retirement payload.

		Returns:
			The retired threshold profile response schema.
		"""
		threshold_profile_model = await self._get_tenant_threshold_profile(
			tenant_id,
			threshold_profile_id,
		)
		effective_to = payload.effective_to or datetime.now(UTC)
		self._validate_retirement_window(
			effective_from=threshold_profile_model.effective_from,
			effective_to=effective_to,
			label='threshold profile',
		)
		if not threshold_profile_model.is_active:
			raise InvalidConfigurationLifecycleError(
				f'Tenant threshold profile "{threshold_profile_id}" is already inactive.'
			)

		updated_threshold_profile_model = (
			await self._uow.tenant_threshold_profiles.update_threshold_profile(
				threshold_profile_id,
				TenantThresholdProfileUpdateSchema(
					is_active=False,
					effective_to=effective_to,
				),
			)
		)
		await self._validate_threshold_profiles(tenant_id)
		await self._uow.commit()
		return TenantThresholdProfileSchema.model_validate(
			updated_threshold_profile_model
		)

	async def create_hash_key_version(
		self,
		tenant_id: UUID,
		payload: TenantHashKeyVersionCreateSchema,
	) -> TenantHashKeyVersionSchema:
		"""Create the next active hash key version for a tenant.

		Args:
			tenant_id: The tenant identifier.
			payload: The hash key version creation payload.

		Returns:
			The created hash key version response schema.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		await self._rollover_hash_key_version(
			tenant_id=tenant_id,
			effective_from=payload.effective_from,
		)
		hash_key_version_model = (
			await self._uow.tenant_hash_key_versions.create_hash_key_version(
				tenant_id,
				payload,
			)
		)
		await self._validate_hash_key_versions(tenant_id)
		await self._uow.commit()
		return TenantHashKeyVersionSchema.model_validate(hash_key_version_model)

	async def list_hash_key_versions(
		self,
		tenant_id: UUID,
		filters: TenantHashKeyVersionFilterParams,
	) -> list[TenantHashKeyVersionSchema]:
		"""Return hash key versions for a tenant.

		Args:
			tenant_id: The tenant identifier.
			filters: The hash key version filter parameters.

		Returns:
			The hash key version response schemas for the tenant.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		hash_key_version_models = (
			await self._uow.tenant_hash_key_versions.list_hash_key_versions_for_tenant(
				tenant_id,
				filters,
			)
		)
		return [
			TenantHashKeyVersionSchema.model_validate(hash_key_version_model)
			for hash_key_version_model in hash_key_version_models
		]

	async def get_hash_key_version(
		self,
		tenant_id: UUID,
		hash_key_version_id: UUID,
	) -> TenantHashKeyVersionSchema:
		"""Return a hash key version for a tenant.

		Args:
			tenant_id: The tenant identifier.
			hash_key_version_id: The hash key version identifier.

		Returns:
			The matching hash key version response schema.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		hash_key_version_model = await self._get_tenant_hash_key_version(
			tenant_id,
			hash_key_version_id,
		)
		return TenantHashKeyVersionSchema.model_validate(hash_key_version_model)

	async def retire_hash_key_version(
		self,
		tenant_id: UUID,
		hash_key_version_id: UUID,
		payload: TenantHashKeyVersionRetireSchema,
	) -> TenantHashKeyVersionSchema:
		"""Retire an active hash key version for a tenant.

		Args:
			tenant_id: The tenant identifier.
			hash_key_version_id: The hash key version identifier.
			payload: The hash key version retirement payload.

		Returns:
			The retired hash key version response schema.
		"""
		hash_key_version_model = await self._get_tenant_hash_key_version(
			tenant_id,
			hash_key_version_id,
		)
		effective_to = payload.effective_to or datetime.now(UTC)
		self._validate_retirement_window(
			effective_from=hash_key_version_model.effective_from,
			effective_to=effective_to,
			label='hash key version',
		)
		if not hash_key_version_model.is_active:
			raise InvalidConfigurationLifecycleError(
				f'Tenant hash key version "{hash_key_version_id}" is already inactive.'
			)

		updated_hash_key_version_model = (
			await self._uow.tenant_hash_key_versions.update_hash_key_version(
				hash_key_version_id,
				TenantHashKeyVersionUpdateSchema(
					is_active=False,
					effective_to=effective_to,
				),
			)
		)
		await self._validate_hash_key_versions(tenant_id)
		await self._uow.commit()
		return TenantHashKeyVersionSchema.model_validate(updated_hash_key_version_model)

	async def _validate_operating_modes(self, tenant_id: UUID) -> None:
		"""Validate active operating mode invariants for a tenant.

		Args:
			tenant_id: The tenant identifier.
		"""
		operating_mode_models = (
			await self._uow.tenant_operating_modes.list_operating_modes_for_tenant(
				tenant_id,
				TenantOperatingModeFilterParams(),
			)
		)
		operating_mode_records = [
			TenantOperatingModeRecord.model_validate(operating_mode_model)
			for operating_mode_model in operating_mode_models
		]
		self._validator.ensure_single_active_operating_mode(operating_mode_records)

	async def _validate_threshold_profiles(self, tenant_id: UUID) -> None:
		"""Validate threshold profile invariants for a tenant.

		Args:
			tenant_id: The tenant identifier.
		"""
		threshold_profile_models = await self._uow.tenant_threshold_profiles.list_threshold_profiles_for_tenant(
			tenant_id,
			TenantThresholdProfileFilterParams(),
		)
		threshold_profiles = [
			TenantThresholdProfile.model_validate(threshold_profile_model)
			for threshold_profile_model in threshold_profile_models
		]
		for threshold_profile in threshold_profiles:
			self._validator.validate_threshold_profile(threshold_profile)
		self._validator.ensure_single_active_threshold_profile(threshold_profiles)

	async def _validate_hash_key_versions(self, tenant_id: UUID) -> None:
		"""Validate hash key version invariants for a tenant.

		Args:
			tenant_id: The tenant identifier.
		"""
		hash_key_version_models = (
			await self._uow.tenant_hash_key_versions.list_hash_key_versions_for_tenant(
				tenant_id,
				TenantHashKeyVersionFilterParams(),
			)
		)
		hash_key_versions = [
			TenantHashKeyVersion.model_validate(hash_key_version_model)
			for hash_key_version_model in hash_key_version_models
		]
		for hash_key_version in hash_key_versions:
			self._validator.validate_hash_key_version(hash_key_version)
		self._validator.ensure_single_active_hash_key_version(hash_key_versions)

	async def _rollover_operating_mode(
		self,
		*,
		tenant_id: UUID,
		effective_from: datetime,
	) -> None:
		"""Deactivate the current active operating mode before creating the next one.

		Args:
			tenant_id: The tenant identifier.
			effective_from: The effective start time of the new record.
		"""
		active_operating_modes = (
			await self._uow.tenant_operating_modes.list_operating_modes_for_tenant(
				tenant_id,
				TenantOperatingModeFilterParams(is_active=True),
			)
		)
		if not active_operating_modes:
			return

		current_active_operating_mode = active_operating_modes[0]
		self._validate_superseding_window(
			current_effective_from=current_active_operating_mode.effective_from,
			next_effective_from=effective_from,
			label='operating mode',
		)
		await self._uow.tenant_operating_modes.update_operating_mode(
			current_active_operating_mode.id,
			TenantOperatingModeUpdateSchema(
				is_active=False,
				effective_to=effective_from,
			),
		)

	async def _rollover_threshold_profile(
		self,
		*,
		tenant_id: UUID,
		effective_from: datetime,
	) -> None:
		"""Deactivate the current active threshold profile before creating the next one.

		Args:
			tenant_id: The tenant identifier.
			effective_from: The effective start time of the new record.
		"""
		active_threshold_profiles = await self._uow.tenant_threshold_profiles.list_threshold_profiles_for_tenant(
			tenant_id,
			TenantThresholdProfileFilterParams(is_active=True),
		)
		if not active_threshold_profiles:
			return

		current_active_threshold_profile = active_threshold_profiles[0]
		self._validate_superseding_window(
			current_effective_from=current_active_threshold_profile.effective_from,
			next_effective_from=effective_from,
			label='threshold profile',
		)
		await self._uow.tenant_threshold_profiles.update_threshold_profile(
			current_active_threshold_profile.id,
			TenantThresholdProfileUpdateSchema(
				is_active=False,
				effective_to=effective_from,
			),
		)

	async def _rollover_hash_key_version(
		self,
		*,
		tenant_id: UUID,
		effective_from: datetime,
	) -> None:
		"""Deactivate the current active hash key version before creating the next one.

		Args:
			tenant_id: The tenant identifier.
			effective_from: The effective start time of the new record.
		"""
		active_hash_key_versions = (
			await self._uow.tenant_hash_key_versions.list_hash_key_versions_for_tenant(
				tenant_id,
				TenantHashKeyVersionFilterParams(is_active=True),
			)
		)
		if not active_hash_key_versions:
			return

		current_active_hash_key_version = active_hash_key_versions[0]
		self._validate_superseding_window(
			current_effective_from=current_active_hash_key_version.effective_from,
			next_effective_from=effective_from,
			label='hash key version',
		)
		await self._uow.tenant_hash_key_versions.update_hash_key_version(
			current_active_hash_key_version.id,
			TenantHashKeyVersionUpdateSchema(
				is_active=False,
				effective_to=effective_from,
			),
		)

	async def _get_tenant_operating_mode(
		self,
		tenant_id: UUID,
		operating_mode_id: UUID,
	):
		"""Return an operating mode that belongs to the given tenant.

		Args:
			tenant_id: The tenant identifier.
			operating_mode_id: The operating mode identifier.

		Returns:
			The matching operating mode model.
		"""
		operating_mode_model = (
			await self._uow.tenant_operating_modes.get_operating_mode_by_id_or_raise(
				operating_mode_id
			)
		)
		self._ensure_same_tenant(
			resource_tenant_id=operating_mode_model.tenant_id,
			tenant_id=tenant_id,
			error_factory=lambda: TenantOperatingModeNotFoundError(
				f'Tenant operating mode "{operating_mode_id}" does not exist.'
			),
		)
		return operating_mode_model

	async def _get_tenant_threshold_profile(
		self,
		tenant_id: UUID,
		threshold_profile_id: UUID,
	):
		"""Return a threshold profile that belongs to the given tenant.

		Args:
			tenant_id: The tenant identifier.
			threshold_profile_id: The threshold profile identifier.

		Returns:
			The matching threshold profile model.
		"""
		threshold_profile_model = await self._uow.tenant_threshold_profiles.get_threshold_profile_by_id_or_raise(
			threshold_profile_id
		)
		self._ensure_same_tenant(
			resource_tenant_id=threshold_profile_model.tenant_id,
			tenant_id=tenant_id,
			error_factory=lambda: TenantThresholdProfileNotFoundError(
				f'Tenant threshold profile "{threshold_profile_id}" does not exist.'
			),
		)
		return threshold_profile_model

	async def _get_tenant_hash_key_version(
		self,
		tenant_id: UUID,
		hash_key_version_id: UUID,
	):
		"""Return a hash key version that belongs to the given tenant.

		Args:
			tenant_id: The tenant identifier.
			hash_key_version_id: The hash key version identifier.

		Returns:
			The matching hash key version model.
		"""
		hash_key_version_model = await self._uow.tenant_hash_key_versions.get_hash_key_version_by_id_or_raise(
			hash_key_version_id
		)
		self._ensure_same_tenant(
			resource_tenant_id=hash_key_version_model.tenant_id,
			tenant_id=tenant_id,
			error_factory=lambda: TenantHashKeyVersionNotFoundError(
				f'Tenant hash key version "{hash_key_version_id}" does not exist.'
			),
		)
		return hash_key_version_model

	@staticmethod
	def _validate_superseding_window(
		*,
		current_effective_from: datetime,
		next_effective_from: datetime,
		label: str,
	) -> None:
		"""Validate the effective window for a superseding record.

		Args:
			current_effective_from: The active record effective start time.
			next_effective_from: The incoming record effective start time.
			label: The configuration label used in the error message.

		Raises:
			InvalidConfigurationLifecycleError: If the next effective time is not
				later than the current active record.
		"""
		if next_effective_from <= current_effective_from:
			raise InvalidConfigurationLifecycleError(
				f'New {label} effective_from must be later than the current active '
				f'{label} effective_from.'
			)

	@staticmethod
	def _validate_retirement_window(
		*,
		effective_from: datetime,
		effective_to: datetime,
		label: str,
	) -> None:
		"""Validate the effective window for a retirement action.

		Args:
			effective_from: The record effective start time.
			effective_to: The requested retirement time.
			label: The configuration label used in the error message.

		Raises:
			InvalidConfigurationLifecycleError: If the retirement time is invalid.
		"""
		if effective_to < effective_from:
			raise InvalidConfigurationLifecycleError(
				f'{label.capitalize()} effective_to must be on or after effective_from.'
			)

	@staticmethod
	def _ensure_same_tenant(
		*,
		resource_tenant_id: UUID,
		tenant_id: UUID,
		error_factory: Callable[[], Exception],
	) -> None:
		"""Ensure a resource belongs to the expected tenant.

		Args:
			resource_tenant_id: The resource tenant identifier.
			tenant_id: The expected tenant identifier.
			error_factory: Factory that builds the domain exception to raise.

		Raises:
			Exception: The domain exception returned by ``error_factory``.
		"""
		if resource_tenant_id != tenant_id:
			raise error_factory()
