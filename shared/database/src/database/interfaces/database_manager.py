from typing import Protocol

from database.interfaces.session_manager import ISessionManager


class IDatabaseManager(Protocol):
	def get_session_manager(self) -> ISessionManager:
		"""Return the initialized session manager."""
		...

	async def initialize(self) -> None:
		"""Initialize the underlying database infrastructure."""
		...

	async def check_connection(self) -> None:
		"""Verify that the database backend is reachable."""
		...

	async def dispose(self) -> None:
		"""Dispose the underlying database resources."""
		...
