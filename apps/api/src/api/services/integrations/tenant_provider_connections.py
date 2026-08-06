import os
from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import (
	DisabledTenantProviderConnectionError,
	InactiveProviderRegistryError,
	InvalidProviderConnectionConfigurationError,
	TenantProviderConnectionNotFoundError,
)
from domain.integration import (
	ProviderConnectionMethod,
	ProviderType,
	TenantProviderConnectionStatus,
)
from integrations import (
	OutboundProviderRegistry,
	ProviderConnectionContext,
	ProviderConnectionSecrets,
)
from schemas.integration import (
	ProviderConnectionTestResultSchema,
	TenantProviderConnectionCreateSchema,
	TenantProviderConnectionFilterParams,
	TenantProviderConnectionSchema,
	TenantProviderConnectionUpdateSchema,
)


class TenantProviderConnectionService:
	def __init__(
		self,
		uow: IUnitOfWork,
		*,
		outbound_provider_registry: OutboundProviderRegistry | None = None,
		environment: Mapping[str, str] | None = None,
	) -> None:
		"""Initialize the tenant provider connection service.

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

	async def create_tenant_provider_connection(
		self,
		tenant_id: UUID,
		payload: TenantProviderConnectionCreateSchema,
	) -> TenantProviderConnectionSchema:
		"""Create a tenant provider connection.

		Args:
			tenant_id: The tenant identifier.
			payload: The tenant provider connection creation payload.

		Returns:
			The created tenant provider connection response schema.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		provider_registry_model = (
			await self._uow.provider_registry.get_provider_registry_by_id_or_raise(
				payload.provider_registry_id
			)
		)

		if not provider_registry_model.is_active:
			raise InactiveProviderRegistryError(
				f'Provider registry entry "{provider_registry_model.id}" is inactive.'
			)

		connection_context = ProviderConnectionContext(
			connection_id=UUID(int=0),
			provider_registry_id=provider_registry_model.id,
			provider_key=provider_registry_model.provider_key,
			display_name=provider_registry_model.display_name,
			connection_name=payload.connection_name,
			base_url=payload.base_url,
			auth_realm=payload.auth_realm,
			client_id=payload.client_id,
			client_secret_ref=payload.client_secret_ref,
			api_token_ref=payload.api_token_ref,
			external_tenant_reference=payload.external_tenant_reference,
			connection_method=provider_registry_model.connection_method,
			supported_policy_actions=tuple(
				provider_registry_model.supported_policy_actions
			),
		)
		self._validate_connection_context(connection_context)

		connection_model = await self._uow.tenant_provider_connections.create_tenant_provider_connection(
			tenant_id,
			payload,
		)
		await self._uow.commit()
		return TenantProviderConnectionSchema.model_validate(connection_model)

	async def list_tenant_provider_connections(
		self,
		tenant_id: UUID,
		filters: TenantProviderConnectionFilterParams,
	) -> list[TenantProviderConnectionSchema]:
		"""Return tenant provider connections for a tenant.

		Args:
			tenant_id: The tenant identifier.
			filters: The tenant provider connection filter parameters.

		Returns:
			The tenant provider connection response schemas for the tenant.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		connection_models = await self._uow.tenant_provider_connections.list_tenant_provider_connections_for_tenant(
			tenant_id,
			filters,
		)
		return [
			TenantProviderConnectionSchema.model_validate(connection_model)
			for connection_model in connection_models
		]

	async def get_tenant_provider_connection(
		self,
		tenant_id: UUID,
		tenant_provider_connection_id: UUID,
	) -> TenantProviderConnectionSchema:
		"""Return a tenant provider connection by identifier.

		Args:
			tenant_id: The tenant identifier.
			tenant_provider_connection_id: The tenant provider connection identifier.

		Returns:
			The matching tenant provider connection response schema.
		"""
		connection_model = await self._get_owned_connection(
			tenant_id,
			tenant_provider_connection_id,
		)
		return TenantProviderConnectionSchema.model_validate(connection_model)

	async def update_tenant_provider_connection(
		self,
		tenant_id: UUID,
		tenant_provider_connection_id: UUID,
		payload: TenantProviderConnectionUpdateSchema,
	) -> TenantProviderConnectionSchema:
		"""Update a tenant provider connection by identifier.

		Args:
			tenant_id: The tenant identifier.
			tenant_provider_connection_id: The tenant provider connection identifier.
			payload: The tenant provider connection update payload.

		Returns:
			The updated tenant provider connection response schema.
		"""
		connection_model = await self._get_owned_connection(
			tenant_id,
			tenant_provider_connection_id,
		)
		provider_registry_model = (
			await self._uow.provider_registry.get_provider_registry_by_id_or_raise(
				connection_model.provider_registry_id
			)
		)
		updates = payload.model_dump(exclude_unset=True)
		effective_payload = TenantProviderConnectionCreateSchema(
			provider_registry_id=connection_model.provider_registry_id,
			connection_name=connection_model.connection_name,
			base_url=connection_model.base_url,
			auth_realm=connection_model.auth_realm,
			client_id=connection_model.client_id,
			client_secret_ref=connection_model.client_secret_ref,
			api_token_ref=connection_model.api_token_ref,
			external_tenant_reference=connection_model.external_tenant_reference,
			status=connection_model.status,
			disabled_at=connection_model.disabled_at,
			last_tested_at=connection_model.last_tested_at,
			last_test_error=connection_model.last_test_error,
		).model_copy(update=updates)

		connection_context = ProviderConnectionContext(
			connection_id=connection_model.id,
			provider_registry_id=provider_registry_model.id,
			provider_key=provider_registry_model.provider_key,
			display_name=provider_registry_model.display_name,
			connection_name=effective_payload.connection_name,
			base_url=effective_payload.base_url,
			auth_realm=effective_payload.auth_realm,
			client_id=effective_payload.client_id,
			client_secret_ref=effective_payload.client_secret_ref,
			api_token_ref=effective_payload.api_token_ref,
			external_tenant_reference=effective_payload.external_tenant_reference,
			connection_method=provider_registry_model.connection_method,
			supported_policy_actions=tuple(
				provider_registry_model.supported_policy_actions
			),
		)
		self._validate_connection_context(connection_context)

		updated_connection_model = await self._uow.tenant_provider_connections.update_tenant_provider_connection(
			tenant_provider_connection_id,
			payload,
		)
		await self._uow.commit()
		return TenantProviderConnectionSchema.model_validate(updated_connection_model)

	async def activate_tenant_provider_connection(
		self,
		tenant_id: UUID,
		tenant_provider_connection_id: UUID,
	) -> TenantProviderConnectionSchema:
		"""Activate a tenant provider connection.

		Args:
			tenant_id: The tenant identifier.
			tenant_provider_connection_id: The tenant provider connection identifier.

		Returns:
			The activated tenant provider connection response schema.
		"""
		connection_model = await self._get_owned_connection(
			tenant_id,
			tenant_provider_connection_id,
		)
		provider_registry_model = (
			await self._uow.provider_registry.get_provider_registry_by_id_or_raise(
				connection_model.provider_registry_id
			)
		)
		if not provider_registry_model.is_active:
			raise InactiveProviderRegistryError(
				f'Provider registry entry "{provider_registry_model.id}" is inactive.'
			)

		await self._ensure_no_other_active_connection_of_type(
			tenant_id=tenant_id,
			provider_type=provider_registry_model.provider_type,
			excluding_connection_id=connection_model.id,
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
		self._validate_connection_context(connection_context)

		updated_connection_model = await self._uow.tenant_provider_connections.update_tenant_provider_connection(
			tenant_provider_connection_id,
			TenantProviderConnectionUpdateSchema(
				status=TenantProviderConnectionStatus.ACTIVE,
				disabled_at=None,
				last_test_error=None,
			),
		)
		await self._uow.commit()
		return TenantProviderConnectionSchema.model_validate(updated_connection_model)

	async def disable_tenant_provider_connection(
		self,
		tenant_id: UUID,
		tenant_provider_connection_id: UUID,
	) -> TenantProviderConnectionSchema:
		"""Disable a tenant provider connection.

		Args:
			tenant_id: The tenant identifier.
			tenant_provider_connection_id: The tenant provider connection identifier.

		Returns:
			The disabled tenant provider connection response schema.

		Raises:
			DisabledTenantProviderConnectionError: If the connection is already
				disabled.
		"""
		connection_model = await self._get_owned_connection(
			tenant_id,
			tenant_provider_connection_id,
		)
		if connection_model.status == TenantProviderConnectionStatus.DISABLED:
			raise DisabledTenantProviderConnectionError(
				f'Tenant provider connection "{tenant_provider_connection_id}" is already disabled.'
			)

		updated_connection_model = await self._uow.tenant_provider_connections.update_tenant_provider_connection(
			tenant_provider_connection_id,
			TenantProviderConnectionUpdateSchema(
				status=TenantProviderConnectionStatus.DISABLED,
				disabled_at=datetime.now(UTC),
			),
		)
		await self._uow.commit()
		return TenantProviderConnectionSchema.model_validate(updated_connection_model)

	async def test_tenant_provider_connection(
		self,
		tenant_id: UUID,
		tenant_provider_connection_id: UUID,
	) -> ProviderConnectionTestResultSchema:
		"""Test a tenant provider connection against the configured provider.

		Args:
			tenant_id: The tenant identifier.
			tenant_provider_connection_id: The tenant provider connection identifier.

		Returns:
			The provider connection test result response schema.
		"""
		connection_model = await self._get_owned_connection(
			tenant_id,
			tenant_provider_connection_id,
		)
		provider_registry_model = (
			await self._uow.provider_registry.get_provider_registry_by_id_or_raise(
				connection_model.provider_registry_id
			)
		)
		if not provider_registry_model.is_active:
			raise InactiveProviderRegistryError(
				f'Provider registry entry "{provider_registry_model.id}" is inactive.'
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
		self._validate_connection_context(connection_context)
		secrets = self._resolve_connection_secrets(connection_context)
		adapter = self._outbound_provider_registry.get_adapter(
			provider_registry_model.provider_key
		)
		test_result = await adapter.test_connection(connection_context, secrets)

		if test_result.success:
			next_status = (
				TenantProviderConnectionStatus.ACTIVE
				if connection_model.status == TenantProviderConnectionStatus.ACTIVE
				else TenantProviderConnectionStatus.DISABLED
			)
		else:
			next_status = TenantProviderConnectionStatus.TEST_FAILED

		updated_connection_model = await self._uow.tenant_provider_connections.update_tenant_provider_connection(
			tenant_provider_connection_id,
			TenantProviderConnectionUpdateSchema(
				status=next_status,
				last_tested_at=test_result.tested_at,
				last_test_error=test_result.error_message,
			),
		)
		await self._uow.commit()
		return ProviderConnectionTestResultSchema(
			connection_id=updated_connection_model.id,
			provider_registry_id=updated_connection_model.provider_registry_id,
			provider_key=provider_registry_model.provider_key,
			success=test_result.success,
			tested_at=test_result.tested_at,
			status=updated_connection_model.status,
			error_code=test_result.error_code,
			error_message=test_result.error_message,
			response_metadata=test_result.response_metadata,
		)

	async def _get_owned_connection(
		self,
		tenant_id: UUID,
		tenant_provider_connection_id: UUID,
	):
		"""Return a tenant provider connection that belongs to the given tenant.

		Args:
			tenant_id: The tenant identifier.
			tenant_provider_connection_id: The tenant provider connection identifier.

		Returns:
			The matching tenant provider connection model.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		connection_model = await self._uow.tenant_provider_connections.get_tenant_provider_connection_by_id_or_raise(
			tenant_provider_connection_id
		)
		if connection_model.tenant_id != tenant_id:
			raise TenantProviderConnectionNotFoundError(
				f'Tenant provider connection "{tenant_provider_connection_id}" does not exist.'
			)

		return connection_model

	async def _ensure_no_other_active_connection_of_type(
		self,
		*,
		tenant_id: UUID,
		provider_type: ProviderType,
		excluding_connection_id: UUID,
	) -> None:
		"""Ensure the tenant does not already have another active connection type.

		Args:
			tenant_id: The tenant identifier.
			provider_type: The provider type being activated.
			excluding_connection_id: The current connection identifier.
		"""
		active_connections = await self._uow.tenant_provider_connections.list_tenant_provider_connections_for_tenant(
			tenant_id,
			TenantProviderConnectionFilterParams(
				status=TenantProviderConnectionStatus.ACTIVE
			),
		)
		for active_connection in active_connections:
			if active_connection.id == excluding_connection_id:
				continue

			active_provider_registry_model = (
				await self._uow.provider_registry.get_provider_registry_by_id_or_raise(
					active_connection.provider_registry_id
				)
			)
			if active_provider_registry_model.provider_type == provider_type:
				raise InvalidProviderConnectionConfigurationError(
					f'Tenant "{tenant_id}" already has an active '
					f'"{provider_type.value}" provider connection.'
				)

	@staticmethod
	def _validate_connection_context(context: ProviderConnectionContext) -> None:
		"""Validate provider connection fields required by the connection method.

		Args:
			context: The provider connection context to validate.
		"""
		if (
			context.connection_method
			is ProviderConnectionMethod.OAUTH_CLIENT_CREDENTIALS
		):
			if not context.auth_realm:
				raise InvalidProviderConnectionConfigurationError(
					'Provider connection auth_realm is required for OAuth client credentials.'
				)
			if not context.client_id:
				raise InvalidProviderConnectionConfigurationError(
					'Provider connection client_id is required for OAuth client credentials.'
				)
			if not context.client_secret_ref:
				raise InvalidProviderConnectionConfigurationError(
					'Provider connection client_secret_ref is required for OAuth client credentials.'
				)

		if (
			context.connection_method is ProviderConnectionMethod.API_TOKEN
			and not context.api_token_ref
		):
			raise InvalidProviderConnectionConfigurationError(
				'Provider connection api_token_ref is required for API token authentication.'
			)

		if context.provider_key == 'keycloak' and not context.auth_realm:
			raise InvalidProviderConnectionConfigurationError(
				'Keycloak provider connections require auth_realm to identify the realm.'
			)

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
		client_secret = None
		if context.client_secret_ref is not None:
			client_secret = self._environment.get(context.client_secret_ref)
			if client_secret is None:
				raise InvalidProviderConnectionConfigurationError(
					f'Provider connection secret reference "{context.client_secret_ref}" '
					f'is not available in the environment.'
				)

		api_token = None
		if context.api_token_ref is not None:
			api_token = self._environment.get(context.api_token_ref)
			if api_token is None:
				raise InvalidProviderConnectionConfigurationError(
					f'Provider connection secret reference "{context.api_token_ref}" '
					f'is not available in the environment.'
				)

		return ProviderConnectionSecrets(
			client_secret=client_secret,
			api_token=api_token,
		)
