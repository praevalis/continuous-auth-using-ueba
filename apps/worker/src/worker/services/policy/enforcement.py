import os
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from database import IUnitOfWork
from domain.enforcement import EnforcementActionStatus, EnforcementActionType
from domain.exceptions import (
	InactiveProviderRegistryError,
	InvalidProviderConnectionConfigurationError,
	NoAvailableTenantProviderConnectionError,
)
from domain.integration import (
	ProviderConnectionMethod,
	ProviderType,
	TenantProviderConnectionStatus,
)
from domain.policy import PolicyAction
from integrations import (
	OutboundActionExecutionRequest,
	OutboundProviderRegistry,
	ProviderConnectionContext,
	ProviderConnectionSecrets,
)
from schemas.enforcement import (
	EnforcementActionCreateSchema,
	EnforcementActionUpdateSchema,
)
from schemas.integration import TenantProviderConnectionFilterParams


class AuthEventEnforcementService:
	def __init__(
		self,
		uow: IUnitOfWork,
		*,
		outbound_provider_registry: OutboundProviderRegistry | None = None,
		environment: Mapping[str, str] | None = None,
	) -> None:
		"""Initialize the auth-event enforcement service.

		Args:
			uow: The request-scoped database unit of work.
			outbound_provider_registry: The outbound provider adapter registry.
			environment: The environment mapping used to resolve secret references.
		"""
		self._uow = uow
		self._outbound_provider_registry = (
			outbound_provider_registry or OutboundProviderRegistry()
		)
		self._environment = environment or os.environ

	async def execute_policy_action(
		self,
		*,
		policy_decision_id: Any,
		risk_score: Any,
		auth_event: Any,
		enforcement_action_type: EnforcementActionType,
	) -> str:
		"""Execute an outbound enforcement action for one policy decision.

		Args:
			policy_decision_id: The persisted policy decision identifier.
			risk_score: The persisted risk score model.
			auth_event: The persisted auth event model.
			enforcement_action_type: The enforcement action type to execute.

		Returns:
			The persisted enforcement action identifier.
		"""
		target_user_identifier = self._extract_target_user_identifier(
			auth_event.normalization_metadata
		)
		if target_user_identifier is None:
			enforcement_action = (
				await self._uow.enforcement_actions.create_enforcement_action(
					EnforcementActionCreateSchema(
						tenant_id=risk_score.tenant_id,
						policy_decision_id=policy_decision_id,
						event_source_id=auth_event.event_source_id,
						action_type=enforcement_action_type,
						target_user_hash=auth_event.user_hash,
						integration_name='unconfigured',
						request_payload_redacted=None,
						status=EnforcementActionStatus.SKIPPED,
						attempt_count=0,
						error_code='missing_target_user_identifier',
						error_message=(
							'No reversible target user identifier was persisted for '
							'this auth event.'
						),
						requested_at=datetime.now(UTC),
						completed_at=datetime.now(UTC),
					)
				)
			)
			return str(enforcement_action.id)

		try:
			(
				connection_model,
				provider_registry_model,
			) = await self._select_connection_for_action(
				tenant_id=risk_score.tenant_id,
				action=self._to_policy_action(enforcement_action_type),
			)
			connection_context = ProviderConnectionContext(
				connection_id=connection_model.id,
				provider_registry_id=provider_registry_model.id,
				provider_key=provider_registry_model.provider_key,
				display_name=provider_registry_model.display_name,
				connection_name=connection_model.connection_name,
				base_url=connection_model.base_url,
				auth_realm=connection_model.auth_realm,
				client_id=connection_model.client_id,
				client_secret_ref=connection_model.client_secret_ref,
				api_token_ref=connection_model.api_token_ref,
				external_tenant_reference=connection_model.external_tenant_reference,
				connection_method=provider_registry_model.connection_method,
				supported_policy_actions=tuple(
					provider_registry_model.supported_policy_actions
				),
			)
			secrets = self._resolve_connection_secrets(connection_context)
			adapter = self._outbound_provider_registry.get_adapter(
				provider_registry_model.provider_key
			)
		except (
			InactiveProviderRegistryError,
			InvalidProviderConnectionConfigurationError,
			NoAvailableTenantProviderConnectionError,
		) as error:
			enforcement_action = (
				await self._uow.enforcement_actions.create_enforcement_action(
					EnforcementActionCreateSchema(
						tenant_id=risk_score.tenant_id,
						policy_decision_id=policy_decision_id,
						event_source_id=auth_event.event_source_id,
						action_type=enforcement_action_type,
						target_user_hash=auth_event.user_hash,
						integration_name='unconfigured',
						request_payload_redacted=None,
						status=EnforcementActionStatus.SKIPPED,
						attempt_count=0,
						error_code='provider_connection_unavailable',
						error_message=str(error),
						requested_at=datetime.now(UTC),
						completed_at=datetime.now(UTC),
					)
				)
			)
			return str(enforcement_action.id)

		enforcement_action = (
			await self._uow.enforcement_actions.create_enforcement_action(
				EnforcementActionCreateSchema(
					tenant_id=risk_score.tenant_id,
					policy_decision_id=policy_decision_id,
					event_source_id=auth_event.event_source_id,
					action_type=enforcement_action_type,
					target_user_hash=auth_event.user_hash,
					integration_name=provider_registry_model.provider_key,
					request_payload_redacted=None,
					status=EnforcementActionStatus.PENDING,
					attempt_count=1,
					requested_at=datetime.now(UTC),
				)
			)
		)

		result = await adapter.execute_action(
			connection_context,
			secrets,
			OutboundActionExecutionRequest(
				action=self._to_policy_action(enforcement_action_type),
				target_user_identifier=target_user_identifier,
				target_user_hash=auth_event.user_hash,
				auth_event_id=auth_event.id,
				policy_decision_id=policy_decision_id,
			),
		)
		updated_enforcement_action = (
			await self._uow.enforcement_actions.update_enforcement_action(
				enforcement_action.id,
				EnforcementActionUpdateSchema(
					request_payload_redacted=(
						None
						if result.request_payload_redacted is None
						and result.response_metadata is None
						else {
							'request': result.request_payload_redacted,
							'response': result.response_metadata,
						}
					),
					status=(
						EnforcementActionStatus.SUCCEEDED
						if result.success
						else EnforcementActionStatus.FAILED
					),
					attempt_count=1,
					external_action_id=result.external_action_id,
					error_code=result.error_code,
					error_message=result.error_message,
					completed_at=result.completed_at,
				),
			)
		)
		return str(updated_enforcement_action.id)

	async def _select_connection_for_action(
		self,
		*,
		tenant_id: Any,
		action: PolicyAction,
	) -> tuple[Any, Any]:
		"""Return the active provider connection eligible for a policy action.

		Args:
			tenant_id: The tenant identifier.
			action: The policy action that must be executed.

		Returns:
			The selected tenant provider connection model and provider registry model.
		"""
		active_connections = await self._uow.tenant_provider_connections.list_tenant_provider_connections_for_tenant(
			tenant_id,
			TenantProviderConnectionFilterParams(
				status=TenantProviderConnectionStatus.ACTIVE
			),
		)

		eligible: list[tuple[Any, Any]] = []
		for connection_model in active_connections:
			provider_registry_model = (
				await self._uow.provider_registry.get_provider_registry_by_id_or_raise(
					connection_model.provider_registry_id
				)
			)
			if not provider_registry_model.is_active:
				continue

			if provider_registry_model.provider_type != ProviderType.IDP:
				continue

			if action not in provider_registry_model.supported_policy_actions:
				continue

			eligible.append((connection_model, provider_registry_model))

		if not eligible:
			raise NoAvailableTenantProviderConnectionError(
				f'No active tenant provider connection supports action "{action.value}" '
				f'for tenant "{tenant_id}".'
			)

		if len(eligible) > 1:
			raise InvalidProviderConnectionConfigurationError(
				f'Multiple active tenant provider connections support action '
				f'"{action.value}" for tenant "{tenant_id}".'
			)

		return eligible[0]

	@staticmethod
	def _extract_target_user_identifier(
		normalization_metadata: dict[str, Any] | None,
	) -> str | None:
		"""Return the reversible provider target identifier for an auth event.

		Args:
			normalization_metadata: The persisted normalization metadata.

		Returns:
			The reversible provider target identifier when present.
		"""
		if normalization_metadata is None:
			return None

		provider_targets = normalization_metadata.get('provider_targets')
		if not isinstance(provider_targets, dict):
			return None

		target_user_identifier = provider_targets.get('user_identifier')
		if not isinstance(target_user_identifier, str) or not target_user_identifier:
			return None

		return target_user_identifier

	@staticmethod
	def _to_policy_action(
		enforcement_action_type: EnforcementActionType,
	) -> PolicyAction:
		"""Return the policy action that maps to an enforcement action type.

		Args:
			enforcement_action_type: The enforcement action type to convert.

		Returns:
			The matching policy action.
		"""
		if enforcement_action_type is EnforcementActionType.STEP_UP_MFA:
			return PolicyAction.STEP_UP_MFA
		if enforcement_action_type is EnforcementActionType.TERMINATE_SESSION:
			return PolicyAction.TERMINATE_SESSION
		return PolicyAction.LOCK_ACCOUNT

	def _resolve_connection_secrets(
		self,
		context: ProviderConnectionContext,
	) -> ProviderConnectionSecrets:
		"""Return resolved provider connection secrets for a context.

		Args:
			context: The provider connection context.

		Returns:
			The resolved provider connection secrets.
		"""
		if (
			context.connection_method
			is ProviderConnectionMethod.OAUTH_CLIENT_CREDENTIALS
		):
			if not context.auth_realm or not context.client_id:
				raise InvalidProviderConnectionConfigurationError(
					'OAuth provider connections require auth_realm and client_id.'
				)
			if not context.client_secret_ref:
				raise InvalidProviderConnectionConfigurationError(
					'OAuth provider connections require client_secret_ref.'
				)
			client_secret = self._environment.get(context.client_secret_ref)
			if client_secret is None:
				raise InvalidProviderConnectionConfigurationError(
					f'Provider connection secret reference "{context.client_secret_ref}" '
					f'is not available in the environment.'
				)
			return ProviderConnectionSecrets(client_secret=client_secret)

		if context.connection_method is ProviderConnectionMethod.API_TOKEN:
			if not context.api_token_ref:
				raise InvalidProviderConnectionConfigurationError(
					'API token provider connections require api_token_ref.'
				)
			api_token = self._environment.get(context.api_token_ref)
			if api_token is None:
				raise InvalidProviderConnectionConfigurationError(
					f'Provider connection secret reference "{context.api_token_ref}" '
					f'is not available in the environment.'
				)
			return ProviderConnectionSecrets(api_token=api_token)

		raise InvalidProviderConnectionConfigurationError(
			f'Unsupported provider connection method "{context.connection_method.value}".'
		)
