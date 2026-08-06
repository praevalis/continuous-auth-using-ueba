from domain.exceptions import InvalidProviderConnectionConfigurationError

from integrations.idp.keycloak import KeycloakOutboundAdapter
from integrations.interfaces.outbound import IOutboundProviderAdapter


class OutboundProviderRegistry:
	"""Resolve outbound provider adapters by stable provider key."""

	def __init__(self) -> None:
		"""Initialize the outbound provider registry."""
		self._adapters: dict[str, IOutboundProviderAdapter] = {
			'keycloak': KeycloakOutboundAdapter(),
		}

	def get_adapter(self, provider_key: str) -> IOutboundProviderAdapter:
		"""Return the outbound adapter registered for a provider key.

		Args:
			provider_key: The stable provider key to resolve.

		Returns:
			The outbound provider adapter.

		Raises:
			InvalidProviderConnectionConfigurationError: If no adapter is registered
				for the provider key.
		"""
		adapter = self._adapters.get(provider_key)
		if adapter is None:
			raise InvalidProviderConnectionConfigurationError(
				f'No outbound adapter is registered for provider "{provider_key}".'
			)

		return adapter
