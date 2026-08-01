from redis.asyncio import Redis

from cache.config import CacheSettings


class CacheManager:
	def __init__(self, settings: CacheSettings) -> None:
		"""Initialize the cache manager.

		Args:
			settings: The cache settings used to build the Redis client.
		"""
		self._settings = settings
		self._client: Redis | None = None

	async def initialize(self) -> None:
		"""Initialize the async Redis client."""
		if self._client is not None:
			return

		self._client = Redis.from_url(
			self._settings.REDIS_URL,
			decode_responses=True,
		)

	async def check_connection(self) -> None:
		"""Verify that the Redis backend is reachable.

		Raises:
			RuntimeError: If the cache manager has not been initialized.
		"""
		client = self.get_client()
		await client.ping()

	def get_client(self) -> Redis:
		"""Return the initialized Redis client.

		Returns:
			The initialized async Redis client.

		Raises:
			RuntimeError: If the cache manager has not been initialized.
		"""
		if self._client is None:
			raise RuntimeError('Cache manager has not been initialized.')

		return self._client

	async def dispose(self) -> None:
		"""Dispose the async Redis client."""
		if self._client is None:
			return

		await self._client.aclose()
		self._client = None
