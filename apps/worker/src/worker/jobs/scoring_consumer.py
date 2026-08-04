import logging
from pathlib import Path
from uuid import UUID

from database import DatabaseManager, SqlAlchemyUnitOfWork
from database.queries import ScoringQueryService
from event_broker import IEventBrokerManager

from worker.core.config import WorkerSettings
from worker.services.policy import AuthEventPolicyService
from worker.services.scoring import AuthEventScoringService

logger = logging.getLogger(__name__)


async def run_auth_event_scoring_job(
	settings: WorkerSettings,
	database_manager: DatabaseManager,
	event_broker_manager: IEventBrokerManager,
) -> None:
	"""Run the auth-event scoring consumer loop.

	Args:
		settings: The worker runtime settings for scoring stream consumption.
		database_manager: The initialized database manager used to create sessions.
		event_broker_manager: The initialized event broker manager used to consume
			and acknowledge scoring jobs.
	"""
	await event_broker_manager.create_consumer_group(
		settings.AUTH_EVENT_SCORING_STREAM_NAME,
		settings.AUTH_EVENT_SCORING_CONSUMER_GROUP,
		mkstream=True,
	)

	session_manager = database_manager.get_session_manager()
	model_run_directory = Path(settings.SCORING_MODEL_RUN_DIRECTORY)

	while True:
		stream_entries = await event_broker_manager.read_group(
			settings.AUTH_EVENT_SCORING_CONSUMER_GROUP,
			settings.AUTH_EVENT_SCORING_CONSUMER_NAME,
			{settings.AUTH_EVENT_SCORING_STREAM_NAME: '>'},
			count=settings.AUTH_EVENT_SCORING_BATCH_SIZE,
			block_ms=settings.AUTH_EVENT_SCORING_BLOCK_MS,
		)
		if not stream_entries:
			continue

		for stream_name, messages in stream_entries:
			session = session_manager.create_session()
			uow = SqlAlchemyUnitOfWork(session)
			query_service = ScoringQueryService(session)
			try:
				scoring_service = AuthEventScoringService(
					uow,
					query_service,
					model_run_directory=model_run_directory,
					history_window_days=settings.SCORING_HISTORY_WINDOW_DAYS,
				)
				policy_service = AuthEventPolicyService(uow)
				for _, fields in messages:
					scoring_result = await scoring_service.process_message(fields)
					await policy_service.process_risk_score(
						UUID(scoring_result.risk_score_id)
					)
			except Exception:
				await uow.rollback()
				logger.exception(
					'Failed to process auth-event scoring stream batch.',
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
					settings.AUTH_EVENT_SCORING_CONSUMER_GROUP,
					[stream_message_id for stream_message_id, _ in messages],
				)
			finally:
				await uow.close()
