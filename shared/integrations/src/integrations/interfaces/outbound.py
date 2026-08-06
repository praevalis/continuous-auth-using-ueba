from typing import Protocol

from integrations.models import (
	OutboundActionExecutionRequest,
	OutboundActionExecutionResult,
	ProviderConnectionContext,
	ProviderConnectionSecrets,
	ProviderConnectionTestResult,
)


class IOutboundProviderAdapter(Protocol):
	"""Protocol implemented by outbound provider adapters."""

	@property
	def provider_key(self) -> str:
		"""Return the stable provider key handled by the adapter."""
		...

	async def test_connection(
		self,
		context: ProviderConnectionContext,
		secrets: ProviderConnectionSecrets,
	) -> ProviderConnectionTestResult:
		"""Validate connectivity and credentials for one provider connection.

		Args:
			context: The provider connection metadata.
			secrets: The resolved provider connection secrets.

		Returns:
			The provider connection test result.
		"""
		...

	async def execute_action(
		self,
		context: ProviderConnectionContext,
		secrets: ProviderConnectionSecrets,
		request: OutboundActionExecutionRequest,
	) -> OutboundActionExecutionResult:
		"""Execute one outbound enforcement action.

		Args:
			context: The provider connection metadata.
			secrets: The resolved provider connection secrets.
			request: The outbound enforcement request.

		Returns:
			The outbound execution result.
		"""
		...
