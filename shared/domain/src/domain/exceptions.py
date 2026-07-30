class DomainError(Exception):
	"""Base exception for domain-layer errors."""


class InvalidThresholdConfigurationError(DomainError):
	"""Raised when threshold configuration is invalid."""


class InvalidOperatingModeTransitionError(DomainError):
	"""Raised when an operating mode transition is invalid."""


class MultipleActiveConfigurationsError(DomainError):
	"""Raised when more than one active configuration exists where only one is allowed."""


class UnsupportedPolicyActionError(DomainError):
	"""Raised when a policy action is incompatible with the current operating mode."""
