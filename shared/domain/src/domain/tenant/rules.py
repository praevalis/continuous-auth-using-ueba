from collections.abc import Iterable
from typing import Protocol

from domain.exceptions import (
	InvalidEventSourceStateError,
	InvalidThresholdConfigurationError,
	MultipleActiveConfigurationsError,
)
from domain.tenant.entities import (
	TenantHashKeyVersion,
	TenantOperatingModeRecord,
	TenantThresholdProfile,
)
from domain.tenant.enums import EventSourceStatus, IngestionCredentialStatus


class IEventSourceRules(Protocol):
	def ensure_can_issue_credentials(self, status: EventSourceStatus) -> None:
		"""Ensure an event source is active before issuing credentials."""
		...

	def should_revoke_credential_on_disable(
		self,
		status: IngestionCredentialStatus,
	) -> bool:
		"""Return whether a credential should be revoked on source disablement."""
		...


class DefaultEventSourceRules:
	@staticmethod
	def ensure_can_issue_credentials(status: EventSourceStatus) -> None:
		"""Ensure an event source is active before issuing credentials.

		Args:
			status: The current event source status.

		Raises:
			InvalidEventSourceStateError: If the event source is disabled.
		"""
		if status != EventSourceStatus.ACTIVE:
			raise InvalidEventSourceStateError(
				'Credentials can only be issued for active event sources.'
			)

	@staticmethod
	def should_revoke_credential_on_disable(
		status: IngestionCredentialStatus,
	) -> bool:
		"""Return whether a credential should be revoked on source disablement.

		Args:
			status: The current ingestion credential status.

		Returns:
			True for active credentials, which are the only credentials that can be
			revoked during source disablement.
		"""
		return status == IngestionCredentialStatus.ACTIVE


class ITenantConfigurationValidator(Protocol):
	def validate_threshold_profile(self, profile: TenantThresholdProfile) -> None:
		"""Validate a tenant threshold profile."""
		...

	def validate_hash_key_version(self, key_version: TenantHashKeyVersion) -> None:
		"""Validate a tenant hash key version."""
		...

	def ensure_single_active_operating_mode(
		self,
		records: Iterable[TenantOperatingModeRecord],
	) -> None:
		"""Ensure at most one active operating mode exists."""
		...

	def ensure_single_active_threshold_profile(
		self,
		profiles: Iterable[TenantThresholdProfile],
	) -> None:
		"""Ensure at most one active threshold profile exists."""
		...

	def ensure_single_active_hash_key_version(
		self,
		key_versions: Iterable[TenantHashKeyVersion],
	) -> None:
		"""Ensure at most one active hash key version exists."""
		...


class DefaultTenantConfigurationValidator:
	@staticmethod
	def _ensure_single_active(items: Iterable[object], label: str) -> None:
		"""Ensure a collection contains at most one active item.

		Args:
			items: Items expected to expose an ``is_active`` attribute.
			label: Human-readable configuration label for error messages.

		Raises:
			MultipleActiveConfigurationsError: If more than one item is active.
		"""
		active_count = sum(1 for item in items if getattr(item, 'is_active', False))
		if active_count > 1:
			raise MultipleActiveConfigurationsError(
				f'Only one active {label} is allowed per tenant.'
			)

	def validate_threshold_profile(self, profile: TenantThresholdProfile) -> None:
		"""Validate threshold profile invariants.

		Args:
			profile: The threshold profile to validate.

		Raises:
			InvalidThresholdConfigurationError: If threshold values are invalid.
		"""
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
		"""Validate hash-key-version invariants.

		Args:
			key_version: The tenant hash key version to validate.

		Raises:
			InvalidThresholdConfigurationError: If the key-version configuration is
				invalid.
		"""
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
		"""Ensure only one operating mode record is active.

		Args:
			records: Operating mode records for a tenant.
		"""
		self._ensure_single_active(records, 'operating mode')

	def ensure_single_active_threshold_profile(
		self,
		profiles: Iterable[TenantThresholdProfile],
	) -> None:
		"""Ensure only one threshold profile is active.

		Args:
			profiles: Threshold profiles for a tenant.
		"""
		self._ensure_single_active(profiles, 'threshold profile')

	def ensure_single_active_hash_key_version(
		self,
		key_versions: Iterable[TenantHashKeyVersion],
	) -> None:
		"""Ensure only one hash key version is active.

		Args:
			key_versions: Hash key versions for a tenant.
		"""
		self._ensure_single_active(key_versions, 'hash key version')
