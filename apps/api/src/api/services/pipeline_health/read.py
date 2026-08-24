from datetime import UTC, datetime, timedelta
from uuid import UUID

from database.queries import PipelineHealthRecord, TenantOperationsQueryService
from domain.tenant import PipelineHealthStatus
from schemas.tenant import (
	PipelineHealthComponentSchema,
	PipelineHealthSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession


class PipelineHealthReadService:
	"""Build computed operational health for a tenant's processing pipeline."""

	def __init__(
		self,
		session: AsyncSession,
		stale_after_minutes: int = 15,
		failure_lookback_hours: int = 24,
	) -> None:
		"""Initialize the pipeline-health read service.

		Args:
			session: The async SQLAlchemy session backing the read queries.
			stale_after_minutes: Age after which active work is considered stale.
			failure_lookback_hours: Recent failure window used for health status.
		"""
		self._query_service = TenantOperationsQueryService(session)
		self._stale_after = timedelta(minutes=stale_after_minutes)
		self._failure_lookback = timedelta(hours=failure_lookback_hours)

	async def get_health(self, tenant_id: UUID) -> PipelineHealthSchema:
		"""Return computed pipeline health for a tenant.

		Args:
			tenant_id: The owning tenant identifier.

		Returns:
			The current ingestion, analysis, and response component health.
		"""
		now = datetime.now(UTC)
		records = await self._query_service.get_pipeline_health(
			tenant_id,
			failure_since=now - self._failure_lookback,
		)
		return PipelineHealthSchema(
			tenant_id=tenant_id,
			generated_at=now,
			components=[self._to_component_schema(record, now) for record in records],
		)

	def _to_component_schema(
		self,
		record: PipelineHealthRecord,
		now: datetime,
	) -> PipelineHealthComponentSchema:
		status, detail = self._calculate_status(record, now)
		return PipelineHealthComponentSchema(
			component=record.component,
			status=status,
			last_activity_at=record.last_activity_at,
			last_success_at=record.last_success_at,
			pending_count=record.pending_count,
			failed_count=record.failed_count,
			detail=detail,
		)

	def _calculate_status(
		self,
		record: PipelineHealthRecord,
		now: datetime,
	) -> tuple[PipelineHealthStatus, str]:
		if record.configured_count == 0:
			return (
				PipelineHealthStatus.NOT_CONFIGURED,
				'No active configuration is available.',
			)

		if record.failed_count > 0:
			return (
				PipelineHealthStatus.DEGRADED,
				f'{record.failed_count} recent operation(s) failed.',
			)

		if record.pending_count > 0:
			return (
				PipelineHealthStatus.DEGRADED,
				f'{record.pending_count} operation(s) are still pending.',
			)

		if record.last_activity_at is None:
			return PipelineHealthStatus.IDLE, 'No activity has been recorded yet.'

		last_activity_at = self._as_utc(record.last_activity_at)
		if now - last_activity_at > self._stale_after:
			return (
				PipelineHealthStatus.DEGRADED,
				'Activity has not been observed within the freshness window.',
			)

		return PipelineHealthStatus.HEALTHY, 'Operating normally.'

	@staticmethod
	def _as_utc(value: datetime) -> datetime:
		if value.tzinfo is None:
			return value.replace(tzinfo=UTC)
		return value.astimezone(UTC)
