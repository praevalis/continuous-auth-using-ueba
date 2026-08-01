from collections.abc import AsyncGenerator
from typing import Annotated

from database import IDatabaseManager, ISessionManager
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.infrastructure import InfrastructureManager
from api.dependencies.infrastructure import get_infrastructure_manager


def get_database_manager(
	infrastructure_manager: Annotated[
		InfrastructureManager, Depends(get_infrastructure_manager)
	],
) -> IDatabaseManager:
	"""Return the shared database manager.

	Args:
		infrastructure_manager: The initialized infrastructure manager dependency.

	Returns:
		The shared database manager.
	"""
	return infrastructure_manager.get_database_manager()


def get_session_manager(
	database_manager: Annotated[IDatabaseManager, Depends(get_database_manager)],
) -> ISessionManager:
	"""Return the shared session manager.

	Args:
		database_manager: The shared database manager dependency.

	Returns:
		The shared session manager.
	"""
	return database_manager.get_session_manager()


async def get_db_session(
	session_manager: Annotated[ISessionManager, Depends(get_session_manager)],
) -> AsyncGenerator[AsyncSession]:
	"""Yield a request-scoped async database session.

	Args:
		session_manager: The shared session manager dependency.

	Yields:
		The async database session scoped to the request.
	"""
	async with session_manager.session_scope() as session:
		yield session
