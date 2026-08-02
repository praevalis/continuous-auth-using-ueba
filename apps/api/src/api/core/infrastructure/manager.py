from cache import ICacheManager
from database import IDatabaseManager
from event_broker import IEventBrokerManager


class InfrastructureManager:
	def __init__(
		self,
		database_manager: IDatabaseManager,
		cache_manager: ICacheManager,
		event_broker_manager: IEventBrokerManager,
	) -> None:
		"""Initialize the infrastructure manager.

		Args:
			database_manager: The shared database manager instance.
			cache_manager: The shared cache manager instance.
			event_broker_manager: The shared event broker manager instance.
		"""
		self._database_manager = database_manager
		self._cache_manager = cache_manager
		self._event_broker_manager = event_broker_manager

	async def initialize(self) -> None:
		"""Initialize all infrastructure resources."""
		await self._database_manager.initialize()
		await self._database_manager.check_connection()
		await self._cache_manager.initialize()
		await self._cache_manager.check_connection()
		await self._event_broker_manager.initialize()
		await self._event_broker_manager.check_connection()

	def get_database_manager(self) -> IDatabaseManager:
		"""Return the database manager.

		Returns:
			The shared database manager instance.
		"""
		return self._database_manager

	def get_cache_manager(self) -> ICacheManager:
		"""Return the cache manager.

		Returns:
			The shared cache manager instance.
		"""
		return self._cache_manager

	def get_event_broker_manager(self) -> IEventBrokerManager:
		"""Return the event broker manager.

		Returns:
			The shared event broker manager instance.
		"""
		return self._event_broker_manager

	async def dispose(self) -> None:
		"""Dispose all managed infrastructure resources."""
		await self._event_broker_manager.dispose()
		await self._cache_manager.dispose()
		await self._database_manager.dispose()
