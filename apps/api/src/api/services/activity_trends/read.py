from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from uuid import UUID

from database.queries import TenantOperationsQueryService
from schemas.scoring import (
	ActivityTrendBucketSchema,
	ActivityTrendFilterParams,
	ActivityTrendSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession


class ActivityTrendReadService:
	"""Read computed activity trends for a tenant."""

	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the activity-trend read service.

		Args:
			session: The async SQLAlchemy session backing the read queries.
		"""
		self._query_service = TenantOperationsQueryService(session)

	async def get_trends(
		self,
		tenant_id: UUID,
		filters: ActivityTrendFilterParams,
	) -> ActivityTrendSchema:
		"""Return zero-filled activity buckets for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: The requested time range and bucket interval.

		Returns:
			Chronologically ordered tenant activity trends.
		"""
		now = datetime.now(UTC)
		occurred_before = filters.occurred_before or now
		default_duration = (
			timedelta(hours=24)
			if filters.interval.value == 'hour'
			else timedelta(days=30)
		)
		occurred_after = filters.occurred_after or occurred_before - default_duration
		effective_filters = filters.model_copy(
			update={
				'occurred_after': occurred_after,
				'occurred_before': occurred_before,
			}
		)
		buckets = await self._query_service.get_activity_trends(
			tenant_id,
			effective_filters,
		)
		return ActivityTrendSchema(
			tenant_id=tenant_id,
			occurred_after=occurred_after,
			occurred_before=occurred_before,
			interval=filters.interval,
			buckets=[
				ActivityTrendBucketSchema.model_validate(asdict(bucket))
				for bucket in buckets
			],
			generated_at=now,
		)
