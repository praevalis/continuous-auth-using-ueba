from contextlib import AbstractAsyncContextManager
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class ISessionManager(Protocol):
	def create_session(self) -> AsyncSession:
		"""Create a new async database session."""
		...

	def session_scope(self) -> AbstractAsyncContextManager[AsyncSession]:
		"""Yield a managed async database session context."""
		...

	async def dispose(self) -> None:
		"""Dispose the underlying engine resources."""
		...
