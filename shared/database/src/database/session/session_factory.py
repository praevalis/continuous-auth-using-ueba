from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


def create_session_factory(
	engine: AsyncEngine,
	*,
	expire_on_commit: bool = False,
) -> async_sessionmaker[AsyncSession]:
	"""Create an async SQLAlchemy session factory.

	Args:
		engine: The async engine bound to produced sessions.
		expire_on_commit: Whether ORM state expires after commit.

	Returns:
		An async session factory bound to the provided engine.
	"""
	return async_sessionmaker(
		bind=engine,
		class_=AsyncSession,
		expire_on_commit=expire_on_commit,
	)
