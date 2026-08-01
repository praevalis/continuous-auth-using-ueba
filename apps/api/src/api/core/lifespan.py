import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from cache import CacheManager
from database import DatabaseManager
from fastapi import FastAPI

from api.core.config import get_api_settings
from api.core.infrastructure import InfrastructureManager
from api.core.logging import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
	"""Manage application startup and shutdown resources.

	Args:
		app: The FastAPI application instance.

	Yields:
		Control back to FastAPI after startup initialization.
	"""
	settings = get_api_settings()
	configure_logging(settings.API_LOG_LEVEL)

	infrastructure_manager = InfrastructureManager(
		database_manager=DatabaseManager(settings.database_settings),
		cache_manager=CacheManager(settings.cache_settings),
	)
	await infrastructure_manager.initialize()
	app.state.infrastructure_manager = infrastructure_manager

	logger.info(
		'API infrastructure initialized.',
		extra={'environment': settings.ENVIRONMENT},
	)

	try:
		yield
	finally:
		await infrastructure_manager.dispose()
		logger.info('API infrastructure disposed.')
