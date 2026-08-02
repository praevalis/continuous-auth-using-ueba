import hashlib
import json
import logging
from datetime import datetime
from uuid import UUID

from database import IUnitOfWork
from schemas.event import AuthEventCreateSchema, AuthEventIngestionMessageSchema

from worker.services.ingestion.anonymization import AuthEventAnonymizationService
from worker.services.ingestion.models import AuthEventNormalizedFields
from worker.services.ingestion.normalization import AuthEventNormalizationService
from worker.services.ingestion.persistence import AuthEventPersistenceService

logger = logging.getLogger(__name__)


class AuthEventIngestionConsumerService:
	def __init__(
		self,
		uow: IUnitOfWork,
		normalization_service: AuthEventNormalizationService,
		anonymization_service: AuthEventAnonymizationService,
		persistence_service: AuthEventPersistenceService,
	) -> None:
		"""Initialize the auth-event ingestion consumer service.

		Args:
			uow: The request-scoped database unit of work used during batch
				normalization and persistence.
			normalization_service: The service that canonicalizes raw ingestion
				messages.
			anonymization_service: The service that hashes and redacts sensitive
				values.
			persistence_service: The service that persists canonical auth events.
		"""
		self._uow = uow
		self._normalization_service = normalization_service
		self._anonymization_service = anonymization_service
		self._persistence_service = persistence_service

	async def process_message(
		self,
		stream_message_id: str,
		fields: dict[str, str],
	) -> None:
		"""Normalize, enrich, and persist a stream-delivered auth event.

		Args:
			stream_message_id: The Redis Stream entry identifier being processed.
			fields: The string-decoded Redis Stream fields for the accepted event.
		"""
		message, auth_event = await self._build_auth_event(
			stream_message_id,
			fields,
		)
		await self._persistence_service.persist(auth_event)

		logger.info(
			'Persisted canonical auth event from ingestion stream message.',
			extra={
				'stream_message_id': stream_message_id,
				'tenant_id': str(message.tenant_id),
				'event_source_id': str(message.event_source_id),
			},
		)

	async def process_messages(
		self,
		messages: list[tuple[str, dict[str, str]]],
	) -> None:
		"""Normalize, enrich, and persist a batch of stream-delivered auth events.

		Args:
			messages: The Redis Stream message identifiers paired with their
				string-decoded fields for one consumed batch.
		"""
		auth_events = []
		stream_message_ids: list[str] = []
		for stream_message_id, fields in messages:
			_, auth_event = await self._build_auth_event(
				stream_message_id,
				fields,
			)
			auth_events.append(auth_event)
			stream_message_ids.append(stream_message_id)

		created_count = await self._persistence_service.persist_batch(auth_events)
		logger.info(
			'Persisted canonical auth-event batch from ingestion stream messages.',
			extra={
				'stream_message_ids': stream_message_ids,
				'batch_size': len(stream_message_ids),
				'created_count': created_count,
			},
		)

	async def _build_auth_event(
		self,
		stream_message_id: str,
		fields: dict[str, str],
	) -> tuple[AuthEventIngestionMessageSchema, AuthEventCreateSchema]:
		"""Build the canonical persistence schema for one stream-delivered event.

		Args:
			stream_message_id: The Redis Stream entry identifier being processed.
			fields: The string-decoded Redis Stream fields for the accepted event.

		Returns:
			The parsed ingestion message and the fully materialized persistence
			schema derived from it.
		"""
		message = AuthEventIngestionMessageSchema(
			tenant_id=UUID(fields['tenant_id']),
			event_source_id=UUID(fields['event_source_id']),
			ingestion_credential_id=UUID(fields['ingestion_credential_id']),
			source_event_id=fields.get('source_event_id') or None,
			occurred_at=datetime.fromisoformat(fields['occurred_at']),
			accepted_at=datetime.fromisoformat(fields['accepted_at']),
			payload_schema_version=int(fields['payload_schema_version']),
			raw_payload=json.loads(fields['raw_payload']),
		)
		hash_key_version_model = await self._uow.tenant_hash_key_versions.get_active_hash_key_version_for_tenant_or_raise(
			message.tenant_id
		)
		normalized_event = await self._normalization_service.normalize(
			message,
			stream_message_id=stream_message_id,
		)
		auth_event = AuthEventCreateSchema(
			tenant_id=normalized_event.tenant_id,
			event_source_id=normalized_event.event_source_id,
			ingestion_credential_id=normalized_event.ingestion_credential_id,
			source_event_id=normalized_event.source_event_id,
			idempotency_key=self._build_idempotency_key(normalized_event),
			occurred_at=normalized_event.occurred_at,
			ingested_at=normalized_event.ingested_at,
			event_type=normalized_event.event_type,
			outcome=normalized_event.outcome,
			user_hash=self._anonymization_service.hash_value(
				normalized_event.user_identifier,
				hash_key_version_model,
			)
			or '',
			account_hash=self._anonymization_service.hash_value(
				normalized_event.account_identifier,
				hash_key_version_model,
			),
			session_hash=self._anonymization_service.hash_value(
				normalized_event.session_identifier,
				hash_key_version_model,
			),
			source_ip_hash=self._anonymization_service.hash_value(
				normalized_event.source_ip,
				hash_key_version_model,
			),
			source_ip_prefix=self._anonymization_service.derive_source_ip_prefix(
				normalized_event.source_ip
			),
			device_hash=self._anonymization_service.hash_value(
				normalized_event.device_identifier,
				hash_key_version_model,
			),
			host_hash=self._anonymization_service.hash_value(
				normalized_event.host_identifier,
				hash_key_version_model,
			),
			auth_method=normalized_event.auth_method,
			failure_reason=normalized_event.failure_reason,
			location_country=normalized_event.location_country,
			location_region=normalized_event.location_region,
			occurred_hour=normalized_event.occurred_hour,
			occurred_day_of_week=normalized_event.occurred_day_of_week,
			hash_key_version=hash_key_version_model.key_version,
			payload_schema_version=normalized_event.payload_schema_version,
			raw_payload_redacted=self._anonymization_service.redact_payload(
				normalized_event.raw_payload
			),
			normalization_metadata=normalized_event.normalization_metadata,
		)
		return message, auth_event

	def _build_idempotency_key(
		self, normalized_event: AuthEventNormalizedFields
	) -> str:
		"""Build a deterministic idempotency key from canonical normalized fields.

		Args:
			normalized_event: The canonical auth-event fields before anonymization.

		Returns:
			A deterministic hex digest representing the normalized event content.
		"""
		hasher = hashlib.sha256()
		hasher.update(str(normalized_event.tenant_id).encode('utf-8'))
		hasher.update(b':')
		hasher.update(str(normalized_event.event_source_id).encode('utf-8'))
		hasher.update(b':')
		hasher.update(str(normalized_event.ingestion_credential_id).encode('utf-8'))
		hasher.update(b':')
		hasher.update((normalized_event.source_event_id or '').encode('utf-8'))
		hasher.update(b':')
		hasher.update(normalized_event.occurred_at.isoformat().encode('utf-8'))
		hasher.update(b':')
		hasher.update(
			json.dumps(
				normalized_event.raw_payload,
				separators=(',', ':'),
				sort_keys=True,
			).encode('utf-8')
		)
		return hasher.hexdigest()
