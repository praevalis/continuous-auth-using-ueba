from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from domain.integration import ProviderConnectionMethod
from domain.policy import PolicyAction


@dataclass(frozen=True, slots=True)
class ProviderConnectionContext:
	"""Describe the provider connection data needed by outbound adapters."""

	connection_id: UUID
	provider_registry_id: UUID
	provider_key: str
	display_name: str
	connection_name: str
	base_url: str
	auth_realm: str | None
	client_id: str | None
	client_secret_ref: str | None
	api_token_ref: str | None
	external_tenant_reference: str | None
	connection_method: ProviderConnectionMethod
	supported_policy_actions: tuple[PolicyAction, ...]


@dataclass(frozen=True, slots=True)
class ProviderConnectionSecrets:
	"""Contain resolved provider connection secrets for one adapter call."""

	client_secret: str | None = None
	api_token: str | None = None


@dataclass(frozen=True, slots=True)
class ProviderConnectionTestResult:
	"""Describe the outcome of validating a provider connection."""

	success: bool
	tested_at: datetime
	error_code: str | None = None
	error_message: str | None = None
	response_metadata: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class OutboundActionExecutionRequest:
	"""Describe one outbound enforcement action execution request."""

	action: PolicyAction
	target_user_identifier: str
	target_user_hash: str
	auth_event_id: UUID
	policy_decision_id: UUID


@dataclass(frozen=True, slots=True)
class OutboundActionExecutionResult:
	"""Describe the outcome of one outbound enforcement action execution."""

	success: bool
	completed_at: datetime
	request_payload_redacted: dict[str, Any] | None = None
	external_action_id: str | None = None
	error_code: str | None = None
	error_message: str | None = None
	response_metadata: dict[str, Any] | None = None
