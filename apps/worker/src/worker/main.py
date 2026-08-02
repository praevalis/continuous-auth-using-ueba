import asyncio
import logging

from database import DatabaseManager
from event_broker import EventBrokerManager

from worker.core.config import get_worker_settings
from worker.core.logging import configure_logging
from worker.jobs import run_auth_event_ingestion_job

logger = logging.getLogger(__name__)


async def run() -> None:
	"""Initialize the worker runtime and run configured job loops."""
	settings = get_worker_settings()
	configure_logging(settings.WORKER_LOG_LEVEL)

	database_manager = DatabaseManager(settings.database_settings)
	event_broker_manager = EventBrokerManager(settings.event_broker_settings)

	await database_manager.initialize()
	await database_manager.check_connection()
	await event_broker_manager.initialize()
	await event_broker_manager.check_connection()

	logger.info('Worker infrastructure initialized.')

	try:
		await run_auth_event_ingestion_job(
			settings,
			database_manager,
			event_broker_manager,
		)
	finally:
		await event_broker_manager.dispose()
		await database_manager.dispose()
		logger.info('Worker infrastructure disposed.')


def main() -> None:
	"""Run the worker application."""
	asyncio.run(run())


if __name__ == '__main__':
	main()
