from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


class SessionManager:
	def __init__(
		self, engine: AsyncEngine, session_factory: async_sessionmaker[AsyncSession]
	) -> None:
		"""Initialize the session manager.

		Args:
			engine: The async engine backing the manager.
			session_factory: The factory used to create async sessions.
		"""
		self._engine = engine
		self._session_factory = session_factory

	def create_session(self) -> AsyncSession:
		"""Create a new async database session.

		Returns:
			A newly created async session.
		"""
		return self._session_factory()

	@asynccontextmanager
	async def session_scope(self) -> AsyncGenerator[AsyncSession]:
		"""Yield a managed async session with commit/rollback handling.

		Yields:
			An async session scoped to the context manager lifetime.
		"""
		session = self.create_session()
		try:
			yield session
			await session.commit()
		except Exception:
			await session.rollback()
			raise
		finally:
			await session.close()

	async def dispose(self) -> None:
		"""Dispose the underlying async engine."""
		await self._engine.dispose()
