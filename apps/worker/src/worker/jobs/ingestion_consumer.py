import logging

from database import DatabaseManager, SqlAlchemyUnitOfWork
from event_broker import IEventBrokerManager

from worker.core.config import WorkerSettings
from worker.services.ingestion import (
	AuthEventAnonymizationService,
	AuthEventIngestionConsumerService,
	AuthEventNormalizationService,
	AuthEventPersistenceService,
	AuthEventScoringDispatchService,
)

logger = logging.getLogger(__name__)


async def run_auth_event_ingestion_job(
	settings: WorkerSettings,
	database_manager: DatabaseManager,
	event_broker_manager: IEventBrokerManager,
) -> None:
	"""Run the auth-event ingestion consumer loop.

	Args:
		settings: The worker runtime settings for stream, consumer, and batching
			behavior.
		database_manager: The initialized shared database manager used to create
			sessions for batch processing.
		event_broker_manager: The initialized shared event broker manager used to
			read and acknowledge stream messages.
	"""
	await event_broker_manager.create_consumer_group(
		settings.AUTH_EVENT_INGESTION_STREAM_NAME,
		settings.AUTH_EVENT_NORMALIZATION_CONSUMER_GROUP,
		mkstream=True,
	)

	session_manager = database_manager.get_session_manager()

	while True:
		stream_entries = await event_broker_manager.read_group(
			settings.AUTH_EVENT_NORMALIZATION_CONSUMER_GROUP,
			settings.AUTH_EVENT_NORMALIZATION_CONSUMER_NAME,
			{settings.AUTH_EVENT_INGESTION_STREAM_NAME: '>'},
			count=settings.AUTH_EVENT_NORMALIZATION_BATCH_SIZE,
			block_ms=settings.AUTH_EVENT_NORMALIZATION_BLOCK_MS,
		)
		if not stream_entries:
			continue

		for stream_name, messages in stream_entries:
			session = session_manager.create_session()
			uow = SqlAlchemyUnitOfWork(session)
			try:
				consumer_service = AuthEventIngestionConsumerService(
					uow,
					AuthEventNormalizationService(),
					AuthEventAnonymizationService(),
					AuthEventPersistenceService(uow),
					AuthEventScoringDispatchService(
						event_broker_manager,
						settings.AUTH_EVENT_SCORING_STREAM_NAME,
					),
				)
				await consumer_service.process_messages(messages)
			except Exception:
				await uow.rollback()
				logger.exception(
					'Failed to process auth-event ingestion stream batch.',
					extra={
						'stream_name': stream_name,
						'stream_message_ids': [
							stream_message_id for stream_message_id, _ in messages
						],
					},
				)
			else:
				await event_broker_manager.acknowledge(
					stream_name,
					settings.AUTH_EVENT_NORMALIZATION_CONSUMER_GROUP,
					[stream_message_id for stream_message_id, _ in messages],
				)
			finally:
				await uow.close()
