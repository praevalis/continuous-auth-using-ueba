from dataclasses import dataclass

from domain.exceptions import (
	ActiveProviderRegistryError,
	DisabledTenantProviderConnectionError,
	DomainError,
	EventSourceNotFoundError,
	InactiveProviderRegistryError,
	IngestionAccessDeniedError,
	IngestionAuthenticationError,
	IngestionCredentialAlreadyExistsError,
	IngestionCredentialNotFoundError,
	InvalidOperatingModeTransitionError,
	InvalidProviderConnectionConfigurationError,
	InvalidThresholdConfigurationError,
	MultipleActiveConfigurationsError,
	NoAvailableTenantProviderConnectionError,
	ProviderRegistryAlreadyExistsError,
	ProviderRegistryNotFoundError,
	TenantAlreadyExistsError,
	TenantHashKeyVersionNotFoundError,
	TenantNotFoundError,
	TenantOperatingModeNotFoundError,
	TenantProviderConnectionNotFoundError,
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

	if isinstance(error, ProviderRegistryAlreadyExistsError):
		return DomainErrorMapping(
			status_code=409,
			error_code='provider_registry_already_exists',
		)

	if isinstance(error, IngestionAuthenticationError):
		return DomainErrorMapping(
			status_code=401,
			error_code='invalid_ingestion_credentials',
		)

	if isinstance(error, IngestionAccessDeniedError):
		return DomainErrorMapping(
			status_code=403,
			error_code='ingestion_access_denied',
		)

	if isinstance(
		error,
		(
			EventSourceNotFoundError,
			IngestionCredentialNotFoundError,
			ProviderRegistryNotFoundError,
			TenantHashKeyVersionNotFoundError,
			TenantNotFoundError,
			TenantOperatingModeNotFoundError,
			TenantProviderConnectionNotFoundError,
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
			InvalidProviderConnectionConfigurationError,
			InvalidThresholdConfigurationError,
			ActiveProviderRegistryError,
			InactiveProviderRegistryError,
			NoAvailableTenantProviderConnectionError,
			UnsupportedPolicyActionError,
			DisabledTenantProviderConnectionError,
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
