from dataclasses import dataclass

from domain.exceptions import (
	DomainError,
	EventSourceNotFoundError,
	IngestionCredentialAlreadyExistsError,
	IngestionCredentialNotFoundError,
	InvalidOperatingModeTransitionError,
	InvalidThresholdConfigurationError,
	MultipleActiveConfigurationsError,
	TenantAlreadyExistsError,
	TenantHashKeyVersionNotFoundError,
	TenantNotFoundError,
	TenantOperatingModeNotFoundError,
	TenantThresholdProfileNotFoundError,
	UnsupportedPolicyActionError,
)


@dataclass(frozen=True, slots=True)
class DomainErrorMapping:
	status_code: int
	error_code: str


def get_domain_error_mapping(error: DomainError) -> DomainErrorMapping:
	"""Resolve the HTTP mapping for a domain exception.

	Args:
		error: The raised domain exception.

	Returns:
		The HTTP status and stable error code for the exception.
	"""
	if isinstance(error, MultipleActiveConfigurationsError):
		return DomainErrorMapping(
			status_code=409,
			error_code='multiple_active_configurations',
		)

	if isinstance(error, TenantAlreadyExistsError):
		return DomainErrorMapping(
			status_code=409,
			error_code='tenant_already_exists',
		)

	if isinstance(error, IngestionCredentialAlreadyExistsError):
		return DomainErrorMapping(
			status_code=409,
			error_code='ingestion_credential_already_exists',
		)

	if isinstance(
		error,
		(
			EventSourceNotFoundError,
			IngestionCredentialNotFoundError,
			TenantHashKeyVersionNotFoundError,
			TenantNotFoundError,
			TenantOperatingModeNotFoundError,
			TenantThresholdProfileNotFoundError,
		),
	):
		return DomainErrorMapping(
			status_code=404,
			error_code='resource_not_found',
		)

	if isinstance(
		error,
		(
			InvalidOperatingModeTransitionError,
			InvalidThresholdConfigurationError,
			UnsupportedPolicyActionError,
		),
	):
		return DomainErrorMapping(
			status_code=400,
			error_code='domain_validation_error',
		)

	return DomainErrorMapping(
		status_code=400,
		error_code='domain_error',
	)
