import hashlib
import ipaddress
from collections.abc import Mapping
from typing import Any

from database.models import TenantHashKeyVersionModel


class AuthEventAnonymizationService:
	_SENSITIVE_KEYS = frozenset(
		{
			'user',
			'user_id',
			'username',
			'principal',
			'principal_name',
			'account',
			'account_id',
			'session',
			'session_id',
			'ip',
			'source_ip',
			'client_ip',
			'device',
			'device_id',
			'device_name',
			'host',
			'hostname',
			'computer',
		}
	)

	def hash_value(
		self,
		value: str | None,
		hash_key_version_model: TenantHashKeyVersionModel,
	) -> str | None:
		"""Return a deterministic tenant-scoped hash for the given value.

		Args:
			value: The raw identifier value to hash.
			hash_key_version_model: The active tenant hash key version used to
				derive the deterministic hash.

		Returns:
			The deterministic hex digest when a value is provided, otherwise
			``None``.
		"""
		if value is None:
			return None

		hasher = hashlib.new(hash_key_version_model.algorithm)
		hasher.update(hash_key_version_model.salt_value.encode('utf-8'))
		hasher.update(b':')
		hasher.update(value.encode('utf-8'))
		return hasher.hexdigest()

	def derive_source_ip_prefix(self, source_ip: str | None) -> str | None:
		"""Return a coarse network prefix for a source IP address.

		Args:
			source_ip: The raw source IP address to reduce to a coarse network
				prefix.

		Returns:
			A /24 prefix for IPv4, a /64 prefix for IPv6, or ``None`` when the
			address is missing or invalid.
		"""
		if source_ip is None:
			return None

		try:
			address = ipaddress.ip_address(source_ip)
		except ValueError:
			return None

		if address.version == 4:
			return str(ipaddress.ip_network(f'{source_ip}/24', strict=False))

		return str(ipaddress.ip_network(f'{source_ip}/64', strict=False))

	def redact_payload(self, payload: Mapping[str, Any]) -> dict[str, Any]:
		"""Return a copy of the payload with sensitive identifiers redacted.

		Args:
			payload: The raw event payload to sanitize for canonical persistence.

		Returns:
			A redacted copy of the payload.
		"""
		redacted: dict[str, Any] = {}
		for key, value in payload.items():
			if key.casefold() in self._SENSITIVE_KEYS:
				redacted[key] = '[redacted]'
				continue

			if isinstance(value, Mapping):
				redacted[key] = self.redact_payload(value)
				continue

			if isinstance(value, list):
				redacted[key] = self._redact_list(value)
				continue

			redacted[key] = value

		return redacted

	def _redact_list(self, values: list[Any]) -> list[Any]:
		redacted_values: list[Any] = []
		for value in values:
			if isinstance(value, Mapping):
				redacted_values.append(self.redact_payload(value))
				continue

			if isinstance(value, list):
				redacted_values.append(self._redact_list(value))
				continue

			redacted_values.append(value)

		return redacted_values
