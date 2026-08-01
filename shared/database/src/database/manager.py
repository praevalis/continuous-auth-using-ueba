from sqlalchemy import text

from database.config import DatabaseSettings
from database.interfaces import ISessionManager
from database.session import (
	AsyncDatabaseConfig,
	SessionManager,
	create_database_engine,
	create_session_factory,
)


class DatabaseManager:
	def __init__(self, settings: DatabaseSettings) -> None:
		"""Initialize the database manager.

		Args:
			settings: The database settings used to build the engine and sessions.
		"""
		self._settings = settings
		self._session_manager: ISessionManager | None = None

	async def initialize(self) -> None:
		"""Initialize the database engine, session factory, and session manager."""
		if self._session_manager is not None:
			return

		config = AsyncDatabaseConfig.from_settings(self._settings)
		engine = create_database_engine(config)
		session_factory = create_session_factory(engine)
		self._session_manager = SessionManager(
			engine=engine,
			session_factory=session_factory,
		)

	async def check_connection(self) -> None:
		"""Verify that the database backend is reachable.

		Raises:
			RuntimeError: If the database manager has not been initialized.
		"""
		session_manager = self.get_session_manager()
		async with session_manager.session_scope() as session:
			await session.execute(text('SELECT 1'))

	def get_session_manager(self) -> ISessionManager:
		"""Return the initialized session manager.

		Returns:
			The initialized session manager.

		Raises:
			RuntimeError: If the database manager has not been initialized.
		"""
		if self._session_manager is None:
			raise RuntimeError('Database manager has not been initialized.')

		return self._session_manager

	async def dispose(self) -> None:
		"""Dispose the underlying database resources."""
		if self._session_manager is None:
			return

		await self._session_manager.dispose()
		self._session_manager = None
