class DomainError(Exception):
	"""Base exception for domain-layer errors."""


class InvalidThresholdConfigurationError(DomainError):
	"""Raised when threshold configuration is invalid."""


class InvalidOperatingModeTransitionError(DomainError):
	"""Raised when an operating mode transition is invalid."""


class InvalidConfigurationLifecycleError(DomainError):
	"""Raised when a historical configuration lifecycle transition is invalid."""


class MultipleActiveConfigurationsError(DomainError):
	"""Raised when more than one active configuration exists where only one is allowed."""


class UnsupportedPolicyActionError(DomainError):
	"""Raised when a policy action is incompatible with the current operating mode."""


class TenantAlreadyExistsError(DomainError):
	"""Raised when attempting to create a tenant with a duplicate slug."""


class TenantNotFoundError(DomainError):
	"""Raised when the requested tenant does not exist."""


class EventSourceNotFoundError(DomainError):
	"""Raised when the requested event source does not exist for the tenant."""


class AuthEventNotFoundError(DomainError):
	"""Raised when the requested auth event does not exist."""


class InvalidEventSourceStateError(DomainError):
	"""Raised when an event source state transition is invalid."""


class TenantOperatingModeNotFoundError(DomainError):
	"""Raised when the requested tenant operating mode does not exist."""


class TenantThresholdProfileNotFoundError(DomainError):
	"""Raised when the requested tenant threshold profile does not exist."""


class EventProcessingRunNotFoundError(DomainError):
	"""Raised when the requested event processing run does not exist."""


class FeatureSnapshotNotFoundError(DomainError):
	"""Raised when the requested feature snapshot does not exist."""


class HostInteractionSnapshotNotFoundError(DomainError):
	"""Raised when the requested host interaction snapshot does not exist."""


class HostInteractionSnapshotAlreadyExistsError(DomainError):
	"""Raised when a duplicate host interaction snapshot is created."""


class RiskScoreNotFoundError(DomainError):
	"""Raised when the requested risk score does not exist."""


class PolicyDecisionNotFoundError(DomainError):
	"""Raised when the requested policy decision does not exist."""


class AlertNotFoundError(DomainError):
	"""Raised when the requested alert does not exist."""


class EnforcementActionNotFoundError(DomainError):
	"""Raised when the requested enforcement action does not exist."""


class TenantHashKeyVersionNotFoundError(DomainError):
	"""Raised when the requested tenant hash key version does not exist."""


class IngestionCredentialAlreadyExistsError(DomainError):
	"""Raised when attempting to create a duplicate ingestion credential."""


class InvalidIngestionCredentialStateError(DomainError):
	"""Raised when an ingestion credential state transition is invalid."""


class IngestionCredentialNotFoundError(DomainError):
	"""Raised when the requested ingestion credential does not exist."""


class IngestionAuthenticationError(DomainError):
	"""Raised when ingestion credential authentication fails."""


class IngestionAccessDeniedError(DomainError):
	"""Raised when an authenticated ingestion request is not allowed."""
