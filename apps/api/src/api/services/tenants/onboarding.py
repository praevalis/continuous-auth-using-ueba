import re
import secrets
from datetime import UTC, datetime

from database import IUnitOfWork
from database.models import (
	TenantHashKeyVersionModel,
	TenantOperatingModeModel,
	TenantThresholdProfileModel,
)
from domain.tenant import (
	TenantHashKeyVersion,
	TenantOperatingModeRecord,
	TenantThresholdProfile,
)
from domain.tenant.rules import DefaultTenantConfigurationValidator
from schemas.onboarding import TenantOnboardingCreateSchema, TenantOnboardingSchema
from schemas.tenant import (
	TenantHashKeyVersionCreateSchema,
	TenantHashKeyVersionSchema,
	TenantOperatingModeCreateSchema,
	TenantOperatingModeSchema,
	TenantSchema,
	TenantThresholdProfileCreateSchema,
	TenantThresholdProfileSchema,
)


class TenantOnboardingService:
	def __init__(self, uow: IUnitOfWork) -> None:
		"""Initialize the onboarding service.

		Args:
			uow: The request-scoped database unit of work.
		"""
		self._uow = uow
		self._validator = DefaultTenantConfigurationValidator()

	async def create_tenant(
		self,
		payload: TenantOnboardingCreateSchema,
	) -> TenantOnboardingSchema:
		"""Create a tenant with its initial bootstrap configuration.

		Args:
			payload: The tenant onboarding payload.

		Returns:
			The created tenant plus the initial active bootstrap records.
		"""
		now = datetime.now(UTC)
		tenant_slug = await self._generate_unique_slug(payload.tenant.display_name)
		tenant_model = await self._uow.tenants.create_tenant(
			payload.tenant,
			slug=tenant_slug,
		)
		operating_mode_model = (
			await self._uow.tenant_operating_modes.create_operating_mode(
				tenant_model.id,
				TenantOperatingModeCreateSchema(
					mode=payload.initial_operating_mode,
					effective_from=now,
					effective_to=None,
					changed_by='system',
					change_reason='Initial tenant onboarding.',
				),
			)
		)

		threshold_profile_model = await self._uow.tenant_threshold_profiles.create_threshold_profile(
			tenant_model.id,
			TenantThresholdProfileCreateSchema(
				name='Default Threshold Profile',
				description='Initial threshold profile created during tenant onboarding.',
				caution_threshold=payload.initial_caution_threshold,
				lockout_threshold=payload.initial_lockout_threshold,
				fusion_alpha=payload.initial_fusion_alpha,
				effective_from=now,
				effective_to=None,
			),
		)
		hash_key_version_model = (
			await self._uow.tenant_hash_key_versions.create_hash_key_version(
				tenant_model.id,
				TenantHashKeyVersionCreateSchema(
					key_version=1,
					algorithm=payload.hash_algorithm,
					salt_value=secrets.token_urlsafe(32),
					effective_from=now,
					effective_to=None,
				),
			)
		)

		self._validate_bootstrap_models(
			operating_mode_model=operating_mode_model,
			threshold_profile_model=threshold_profile_model,
			hash_key_version_model=hash_key_version_model,
		)
		await self._uow.commit()
		return TenantOnboardingSchema(
			tenant=TenantSchema.model_validate(tenant_model),
			operating_mode=TenantOperatingModeSchema.model_validate(
				operating_mode_model
			),
			threshold_profile=TenantThresholdProfileSchema.model_validate(
				threshold_profile_model
			),
			hash_key_version=TenantHashKeyVersionSchema.model_validate(
				hash_key_version_model
			),
		)

	async def _generate_unique_slug(self, display_name: str) -> str:
		"""Generate a unique immutable slug from the tenant display name.

		Args:
			display_name: The tenant display name to normalize.

		Returns:
			A unique kebab-case slug suitable for stable tenant identification.
		"""
		base_slug = re.sub(r'[^a-z0-9]+', '-', display_name.casefold()).strip('-')
		if not base_slug:
			base_slug = 'tenant'

		candidate_slug = base_slug
		suffix = 2

		while await self._uow.tenants.get_tenant_by_slug(candidate_slug) is not None:
			candidate_slug = f'{base_slug}-{suffix}'
			suffix += 1

		return candidate_slug

	def _validate_bootstrap_models(
		self,
		*,
		operating_mode_model: TenantOperatingModeModel,
		threshold_profile_model: TenantThresholdProfileModel,
		hash_key_version_model: TenantHashKeyVersionModel,
	) -> None:
		"""Validate bootstrap invariants for the newly created tenant records.

		Args:
			operating_mode_model: The persisted operating mode model to validate.
			threshold_profile_model: The persisted threshold profile model to
				validate.
			hash_key_version_model: The persisted hash key version model to validate.
		"""
		operating_mode = TenantOperatingModeRecord.model_validate(
			operating_mode_model,
		)
		threshold_profile = TenantThresholdProfile.model_validate(
			threshold_profile_model,
		)
		hash_key_version = TenantHashKeyVersion.model_validate(
			hash_key_version_model,
		)

		self._validator.validate_threshold_profile(threshold_profile)
		self._validator.validate_hash_key_version(hash_key_version)
		self._validator.ensure_single_active_operating_mode([operating_mode])
		self._validator.ensure_single_active_threshold_profile([threshold_profile])
		self._validator.ensure_single_active_hash_key_version([hash_key_version])
