import hashlib
import json
import secrets
from datetime import UTC, datetime
from uuid import UUID

from database import IUnitOfWork
from database.models import EventSourceModel
from domain.exceptions import (
	IngestionAccessDeniedError,
	IngestionAuthenticationError,
)
from domain.tenant import (
	EventSourceStatus,
	IngestionCredentialStatus,
	TenantStatus,
)
from event_broker import IEventBrokerManager
from schemas.event import (
	AuthEventIngestionAcceptedSchema,
	AuthEventIngestionRequestSchema,
)


class AuthEventIngestionService:
	def __init__(
		self,
		uow: IUnitOfWork,
		event_broker_manager: IEventBrokerManager,
		auth_event_ingestion_stream_name: str,
	) -> None:
		"""Initialize the auth-event ingestion service.

		Args:
			uow: The request-scoped database unit of work.
			event_broker_manager: The shared event broker manager.
			auth_event_ingestion_stream_name: The Redis Stream name used for
				authentication-event ingestion handoff.
		"""
		self._uow = uow
		self._event_broker_manager = event_broker_manager
		self._auth_event_ingestion_stream_name = auth_event_ingestion_stream_name

	async def ingest_event(
		self,
		payload: AuthEventIngestionRequestSchema,
		*,
		key_id: str,
		key_secret: str,
	) -> AuthEventIngestionAcceptedSchema:
		"""Validate an auth-event ingestion request.

		Args:
			payload: The raw ingestion request payload.
			key_id: The public ingestion credential key identifier.
			key_secret: The plaintext ingestion credential secret.

		Returns:
			The accepted-ingestion acknowledgement payload.
		"""
		credential_model = (
			await self._uow.ingestion_credentials.get_ingestion_credential_by_key_id(
				key_id
			)
		)
		if credential_model is None:
			raise IngestionAuthenticationError('Invalid ingestion credentials.')

		provided_key_hash = hashlib.sha256(key_secret.encode('utf-8')).hexdigest()
		if not secrets.compare_digest(credential_model.key_hash, provided_key_hash):
			raise IngestionAuthenticationError('Invalid ingestion credentials.')

		if credential_model.status != IngestionCredentialStatus.ACTIVE:
			raise IngestionAccessDeniedError(
				'Ingestion credential is not active for event ingestion.'
			)

		now = datetime.now(UTC)
		if (
			credential_model.expires_at is not None
			and credential_model.expires_at <= now
		):
			raise IngestionAccessDeniedError('Ingestion credential has expired.')

		tenant_model = await self._uow.tenants.get_active_tenant_by_id_or_raise(
			credential_model.tenant_id
		)
		if tenant_model.status != TenantStatus.ACTIVE:
			raise IngestionAccessDeniedError(
				'Tenant is not active for event ingestion.'
			)

		event_source_model = await self._resolve_event_source(
			payload=payload,
			credential_tenant_id=credential_model.tenant_id,
			credential_event_source_id=credential_model.event_source_id,
		)
		await self._publish_ingestion_event(
			payload=payload,
			tenant_id=tenant_model.id,
			event_source_id=event_source_model.id,
			ingestion_credential_id=credential_model.id,
			accepted_at=now,
		)

		return AuthEventIngestionAcceptedSchema(
			tenant_id=tenant_model.id,
			event_source_id=event_source_model.id,
			ingestion_credential_id=credential_model.id,
			accepted_at=now,
		)

	async def _resolve_event_source(
		self,
		*,
		payload: AuthEventIngestionRequestSchema,
		credential_tenant_id: UUID,
		credential_event_source_id: UUID | None,
	) -> EventSourceModel:
		"""Resolve and validate the effective event source for an ingestion request.

		Args:
			payload: The raw ingestion request payload.
			credential_tenant_id: The authenticated credential tenant identifier.
			credential_event_source_id: The optional event source bound to the
				authenticated credential.

		Returns:
			The resolved event source model.
		"""
		resolved_event_source_id = payload.event_source_id
		if credential_event_source_id is not None:
			if (
				resolved_event_source_id is not None
				and resolved_event_source_id != credential_event_source_id
			):
				raise IngestionAccessDeniedError(
					'Ingestion credential is not allowed to submit events for the '
					'requested event source.'
				)
			resolved_event_source_id = credential_event_source_id

		if resolved_event_source_id is None:
			raise IngestionAccessDeniedError(
				'An event source is required for event ingestion.'
			)

		event_source_model = await self._uow.event_sources.get_event_source_by_id(
			resolved_event_source_id
		)
		if event_source_model is None:
			raise IngestionAccessDeniedError(
				'Event source is not available for event ingestion.'
			)
		if event_source_model.tenant_id != credential_tenant_id:
			raise IngestionAccessDeniedError(
				'Event source is not available for event ingestion.'
			)
		if event_source_model.status != EventSourceStatus.ACTIVE:
			raise IngestionAccessDeniedError(
				'Event source is not active for event ingestion.'
			)

		return event_source_model

	async def _publish_ingestion_event(
		self,
		*,
		payload: AuthEventIngestionRequestSchema,
		tenant_id: UUID,
		event_source_id: UUID,
		ingestion_credential_id: UUID,
		accepted_at: datetime,
	) -> None:
		"""Publish a validated ingestion request to the auth-event stream.

		Args:
			payload: The raw ingestion request payload.
			tenant_id: The validated tenant identifier.
			event_source_id: The validated event source identifier.
			ingestion_credential_id: The validated ingestion credential identifier.
			accepted_at: The timestamp at which the request was accepted.
		"""
		await self._event_broker_manager.publish(
			self._auth_event_ingestion_stream_name,
			{
				'tenant_id': str(tenant_id),
				'event_source_id': str(event_source_id),
				'ingestion_credential_id': str(ingestion_credential_id),
				'source_event_id': payload.source_event_id or '',
				'occurred_at': payload.occurred_at.isoformat(),
				'accepted_at': accepted_at.isoformat(),
				'payload_schema_version': payload.payload_schema_version,
				'raw_payload': json.dumps(
					payload.raw_payload,
					separators=(',', ':'),
					sort_keys=True,
				),
			},
		)
