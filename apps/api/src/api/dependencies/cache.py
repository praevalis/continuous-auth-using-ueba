from typing import Annotated

from cache import ICacheManager
from fastapi import Depends
from redis.asyncio import Redis

from api.core.infrastructure import InfrastructureManager
from api.dependencies.infrastructure import get_infrastructure_manager


def get_cache_manager(
	infrastructure_manager: Annotated[
		InfrastructureManager, Depends(get_infrastructure_manager)
	],
) -> ICacheManager:
	"""Return the shared cache manager.

	Args:
		infrastructure_manager: The initialized infrastructure manager dependency.

	Returns:
		The shared cache manager.
	"""
	return infrastructure_manager.get_cache_manager()


def get_redis_client(
	cache_manager: Annotated[ICacheManager, Depends(get_cache_manager)],
) -> Redis:
	"""Return the initialized async Redis client.

	Args:
		cache_manager: The shared cache manager dependency.

	Returns:
		The initialized async Redis client.
	"""
	return cache_manager.get_client()
