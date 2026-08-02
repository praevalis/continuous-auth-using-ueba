from domain.tenant import OperatingMode
from pydantic import Field

from schemas.base import SchemaModel
from schemas.tenant import (
	TenantCreateSchema,
	TenantHashKeyVersionSchema,
	TenantOperatingModeSchema,
	TenantSchema,
	TenantThresholdProfileSchema,
)


class TenantOnboardingCreateSchema(SchemaModel):
	tenant: TenantCreateSchema
	initial_operating_mode: OperatingMode = OperatingMode.SHADOW
	initial_caution_threshold: float = Field(default=0.349, ge=0.0)
	initial_lockout_threshold: float = Field(default=0.463, ge=0.0)
	initial_fusion_alpha: float | None = Field(default=None, ge=0.0, le=1.0)
	hash_algorithm: str = Field(default='sha256', min_length=1)


class TenantOnboardingSchema(SchemaModel):
	tenant: TenantSchema
	operating_mode: TenantOperatingModeSchema
	threshold_profile: TenantThresholdProfileSchema
	hash_key_version: TenantHashKeyVersionSchema
