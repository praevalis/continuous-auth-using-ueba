from typing import Any

from domain.event import AuthEventOutcome
from schemas.event import AuthEventIngestionMessageSchema

from worker.services.ingestion.models import AuthEventNormalizedFields


class AuthEventNormalizationService:
	async def normalize(
		self,
		message: AuthEventIngestionMessageSchema,
		*,
		stream_message_id: str,
	) -> AuthEventNormalizedFields:
		"""Normalize a raw ingestion message into canonical pre-anonymized fields.

		Args:
			message: The accepted raw ingestion message consumed from Redis Streams.
			stream_message_id: The Redis Stream entry identifier for traceability.

		Returns:
			The canonical auth-event fields before anonymization and idempotency
			enrichment.

		Raises:
			ValueError: If a required normalized field cannot be derived from the
				raw payload.
		"""
		raw_payload = message.raw_payload
		user_identifier, user_source_key = self._extract_required_value(
			raw_payload,
			'user_id',
			'user',
			'username',
			'principal',
			'principal_name',
		)
		account_identifier, account_source_key = self._extract_optional_value(
			raw_payload,
			'account_id',
			'account',
		)
		session_identifier, session_source_key = self._extract_optional_value(
			raw_payload,
			'session_id',
			'session',
		)
		source_ip, source_ip_source_key = self._extract_optional_value(
			raw_payload,
			'source_ip',
			'client_ip',
			'ip',
		)
		device_identifier, device_source_key = self._extract_optional_value(
			raw_payload,
			'device_id',
			'device',
			'device_name',
		)
		host_identifier, host_source_key = self._extract_optional_value(
			raw_payload,
			'host',
			'hostname',
			'computer',
		)
		event_type, event_type_source_key = self._extract_optional_value(
			raw_payload,
			'event_type',
			'type',
			'action',
			'event_name',
		)
		outcome_value, outcome_source_key = self._extract_optional_value(
			raw_payload,
			'outcome',
			'result',
			'status',
		)
		auth_method, auth_method_source_key = self._extract_optional_value(
			raw_payload,
			'auth_method',
			'method',
			'authentication_method',
		)
		failure_reason, failure_reason_source_key = self._extract_optional_value(
			raw_payload,
			'failure_reason',
			'error_reason',
			'reason',
		)
		location_country, country_source_key = self._extract_optional_value(
			raw_payload,
			'location.country',
			'country',
		)
		location_region, region_source_key = self._extract_optional_value(
			raw_payload,
			'location.region',
			'region',
		)

		return AuthEventNormalizedFields(
			tenant_id=message.tenant_id,
			event_source_id=message.event_source_id,
			ingestion_credential_id=message.ingestion_credential_id,
			source_event_id=message.source_event_id,
			occurred_at=message.occurred_at,
			ingested_at=message.accepted_at,
			event_type=event_type or 'authentication',
			outcome=self._normalize_outcome(outcome_value),
			user_identifier=user_identifier,
			account_identifier=account_identifier,
			session_identifier=session_identifier,
			source_ip=source_ip,
			device_identifier=device_identifier,
			host_identifier=host_identifier,
			auth_method=auth_method,
			failure_reason=failure_reason,
			location_country=location_country,
			location_region=location_region,
			occurred_hour=message.occurred_at.hour,
			occurred_day_of_week=message.occurred_at.weekday(),
			payload_schema_version=message.payload_schema_version,
			raw_payload=raw_payload,
			normalization_metadata={
				'stream_message_id': stream_message_id,
				# TO-DO: Move reversible provider-target identifiers into a dedicated
				# encrypted store instead of persisting them in normalization metadata.
				'provider_targets': {
					'user_identifier': user_identifier,
				},
				'field_sources': {
					'user_identifier': user_source_key,
					'account_identifier': account_source_key,
					'session_identifier': session_source_key,
					'source_ip': source_ip_source_key,
					'device_identifier': device_source_key,
					'host_identifier': host_source_key,
					'event_type': event_type_source_key,
					'outcome': outcome_source_key,
					'auth_method': auth_method_source_key,
					'failure_reason': failure_reason_source_key,
					'location_country': country_source_key,
					'location_region': region_source_key,
				},
			},
		)

	def _extract_required_value(
		self,
		payload: dict[str, Any],
		*keys: str,
	) -> tuple[str, str]:
		"""Return the first matching required payload value and its source key.

		Args:
			payload: The raw payload to inspect.
			*keys: Candidate key paths to resolve in order.

		Returns:
			The resolved string value and the key path that produced it.

		Raises:
			ValueError: If none of the candidate keys yields a value.
		"""
		value, key = self._extract_optional_value(payload, *keys)
		if value is None or key is None:
			raise ValueError(
				f'Missing required normalized field source. Expected one of: {keys}.'
			)

		return value, key

	def _extract_optional_value(
		self,
		payload: dict[str, Any],
		*keys: str,
	) -> tuple[str | None, str | None]:
		"""Return the first matching optional payload value and its source key.

		Args:
			payload: The raw payload to inspect.
			*keys: Candidate key paths to resolve in order.

		Returns:
			The resolved string value and source key path when found, otherwise a
			pair of ``None`` values.
		"""
		for key in keys:
			value = self._resolve_key_path(payload, key)
			if value is None:
				continue
			if isinstance(value, str):
				return value, key
			if isinstance(value, (int, float, bool)):
				return str(value), key

		return None, None

	def _resolve_key_path(self, payload: dict[str, Any], key_path: str) -> Any:
		"""Resolve a dot-delimited key path within a nested payload mapping.

		Args:
			payload: The raw payload to traverse.
			key_path: The dot-delimited key path to resolve.

		Returns:
			The resolved value when present, otherwise ``None``.
		"""
		current: Any = payload
		for segment in key_path.split('.'):
			if not isinstance(current, dict) or segment not in current:
				return None
			current = current[segment]

		return current

	def _normalize_outcome(self, outcome_value: str | None) -> AuthEventOutcome:
		"""Normalize a free-form outcome value into the canonical enum.

		Args:
			outcome_value: The raw outcome value from the payload, if present.

		Returns:
			The canonical authentication-event outcome.
		"""
		if outcome_value is None:
			return AuthEventOutcome.UNKNOWN

		normalized_outcome = outcome_value.casefold()
		if normalized_outcome in {'success', 'succeeded', 'ok', 'allow', 'allowed'}:
			return AuthEventOutcome.SUCCESS
		if normalized_outcome in {'failure', 'failed', 'deny', 'denied', 'error'}:
			return AuthEventOutcome.FAILURE
		if normalized_outcome in {'challenge', 'mfa', 'step_up', 'step-up'}:
			return AuthEventOutcome.CHALLENGE
		if normalized_outcome in {'logout', 'signed_out', 'sign_out'}:
			return AuthEventOutcome.LOGOUT

		return AuthEventOutcome.UNKNOWN
