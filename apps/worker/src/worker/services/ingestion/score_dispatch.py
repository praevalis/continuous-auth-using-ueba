import json

from event_broker import IEventBrokerManager
from schemas.event import AuthEventScoringJobSchema


class AuthEventScoringDispatchService:
	def __init__(
		self,
		event_broker_manager: IEventBrokerManager,
		scoring_stream_name: str,
	) -> None:
		"""Initialize the auth-event scoring dispatch service.

		Args:
			event_broker_manager: The shared event broker manager used to publish
				scoring jobs.
			scoring_stream_name: The Redis Stream name used for scoring work items.
		"""
		self._event_broker_manager = event_broker_manager
		self._scoring_stream_name = scoring_stream_name

	async def dispatch_jobs(
		self,
		jobs: list[AuthEventScoringJobSchema],
	) -> int:
		"""Publish scoring jobs for newly created auth events.

		Args:
			jobs: The scoring jobs to publish.

		Returns:
			The number of published scoring jobs.
		"""
		for job in jobs:
			await self._event_broker_manager.publish(
				self._scoring_stream_name,
				{
					'auth_event_id': str(job.auth_event_id),
					'tenant_id': str(job.tenant_id),
					'payload': json.dumps(
						job.model_dump(mode='json'),
						separators=(',', ':'),
						sort_keys=True,
					),
				},
			)

		return len(jobs)
