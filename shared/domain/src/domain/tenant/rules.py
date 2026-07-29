from collections.abc import Iterable
from typing import Protocol

from domain.exceptions import (
	InvalidThresholdConfigurationError,
	MultipleActiveConfigurationsError,
)
from domain.tenant.entities import (
	TenantHashKeyVersion,
	TenantOperatingModeRecord,
	TenantThresholdProfile,
)


class ITenantConfigurationValidator(Protocol):
	def validate_threshold_profile(self, profile: TenantThresholdProfile) -> None: ...

	def validate_hash_key_version(self, key_version: TenantHashKeyVersion) -> None: ...

	def ensure_single_active_operating_mode(
		self,
		records: Iterable[TenantOperatingModeRecord],
	) -> None: ...

	def ensure_single_active_threshold_profile(
		self,
		profiles: Iterable[TenantThresholdProfile],
	) -> None: ...

	def ensure_single_active_hash_key_version(
		self,
		key_versions: Iterable[TenantHashKeyVersion],
	) -> None: ...


class DefaultTenantConfigurationValidator:
	@staticmethod
	def _ensure_single_active(items: Iterable[object], label: str) -> None:
		active_count = sum(1 for item in items if getattr(item, 'is_active', False))
		if active_count > 1:
			raise MultipleActiveConfigurationsError(
				f'Only one active {label} is allowed per tenant.'
			)

	def validate_threshold_profile(self, profile: TenantThresholdProfile) -> None:
		if profile.caution_threshold < 0 or profile.lockout_threshold < 0:
			raise InvalidThresholdConfigurationError('Thresholds must be non-negative.')
		if profile.caution_threshold >= profile.lockout_threshold:
			raise InvalidThresholdConfigurationError(
				'Caution threshold must be lower than lockout threshold.'
			)
		if profile.fusion_alpha is not None and not 0.0 <= profile.fusion_alpha <= 1.0:
			raise InvalidThresholdConfigurationError(
				'Fusion alpha must be between 0.0 and 1.0.'
			)

	def validate_hash_key_version(self, key_version: TenantHashKeyVersion) -> None:
		if key_version.key_version < 1:
			raise InvalidThresholdConfigurationError(
				'Hash key version must start at 1 or greater.'
			)
		if not key_version.salt_value:
			raise InvalidThresholdConfigurationError('Salt value must not be empty.')

	def ensure_single_active_operating_mode(
		self,
		records: Iterable[TenantOperatingModeRecord],
	) -> None:
		self._ensure_single_active(records, 'operating mode')

	def ensure_single_active_threshold_profile(
		self,
		profiles: Iterable[TenantThresholdProfile],
	) -> None:
		self._ensure_single_active(profiles, 'threshold profile')

	def ensure_single_active_hash_key_version(
		self,
		key_versions: Iterable[TenantHashKeyVersion],
	) -> None:
		self._ensure_single_active(key_versions, 'hash key version')
