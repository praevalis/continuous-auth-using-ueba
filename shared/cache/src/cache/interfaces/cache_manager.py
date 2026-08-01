from typing import Protocol

from redis.asyncio import Redis


class ICacheManager(Protocol):
	async def initialize(self) -> None:
		"""Initialize the underlying cache client."""
		...

	async def check_connection(self) -> None:
		"""Verify that the cache backend is reachable."""
		...

	def get_client(self) -> Redis:
		"""Return the initialized async Redis client."""
		...

	async def dispose(self) -> None:
		"""Dispose the underlying cache resources."""
		...
