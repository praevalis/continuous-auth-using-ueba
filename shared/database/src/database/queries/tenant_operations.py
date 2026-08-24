from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from domain.enforcement import EnforcementActionStatus
from domain.integration import TenantProviderConnectionStatus
from domain.policy import ScoreBand
from domain.scoring import ActivityTrendInterval, ProcessingJobType, ProcessingRunStatus
from domain.tenant import EventSourceStatus, PipelineComponent
from schemas.scoring import ActivityTrendFilterParams
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
	AlertModel,
	AuthEventModel,
	EnforcementActionModel,
	EventProcessingRunModel,
	EventSourceModel,
	PolicyDecisionModel,
	RiskScoreModel,
	TenantProviderConnectionModel,
)


@dataclass(slots=True)
class PipelineHealthRecord:
	"""Aggregated persistence facts used to calculate pipeline health."""

	component: PipelineComponent
	configured_count: int
	last_activity_at: datetime | None
	last_success_at: datetime | None
	pending_count: int
	failed_count: int


@dataclass(slots=True)
class ActivityTrendBucketRecord:
	"""Aggregated tenant activity for one UTC time bucket."""

	bucket_start: datetime
	bucket_end: datetime
	event_count: int = 0
	scored_count: int = 0
	safe_count: int = 0
	caution_count: int = 0
	lockout_count: int = 0
	unscored_count: int = 0
	decision_count: int = 0
	alert_count: int = 0
	response_count: int = 0


class TenantOperationsQueryService:
	"""Read queries for tenant pipeline health and activity trends."""

	def __init__(self, session: AsyncSession) -> None:
		"""Initialize tenant operations queries.

		Args:
			session: The async SQLAlchemy session backing the read queries.
		"""
		self._session = session

	async def get_pipeline_health(
		self,
		tenant_id: UUID,
		failure_since: datetime,
	) -> list[PipelineHealthRecord]:
		"""Return persistence facts for each tenant pipeline component.

		Args:
			tenant_id: The owning tenant identifier.
		failure_since: The lower bound for recent failure counts.

		Returns:
			Aggregated ingestion, analysis, and response pipeline facts.
		"""
		ingestion_result = await self._session.execute(
			select(
				func.count(func.distinct(EventSourceModel.id)),
				func.max(AuthEventModel.occurred_at),
			)
			.select_from(EventSourceModel)
			.outerjoin(
				AuthEventModel,
				AuthEventModel.event_source_id == EventSourceModel.id,
			)
			.where(
				EventSourceModel.tenant_id == tenant_id,
				EventSourceModel.status == EventSourceStatus.ACTIVE,
			)
		)
		active_source_count, latest_event_at = ingestion_result.one()

		analysis_result = await self._session.execute(
			select(
				func.max(EventProcessingRunModel.created_at),
				func.max(EventProcessingRunModel.finished_at).filter(
					EventProcessingRunModel.status == ProcessingRunStatus.SUCCEEDED
				),
				func.count().filter(
					EventProcessingRunModel.status.in_(
						(ProcessingRunStatus.QUEUED, ProcessingRunStatus.RUNNING)
					)
				),
				func.count().filter(
					and_(
						EventProcessingRunModel.status.in_(
							(
								ProcessingRunStatus.FAILED,
								ProcessingRunStatus.DEAD_LETTERED,
							)
						),
						EventProcessingRunModel.created_at >= failure_since,
					)
				),
			).where(
				EventProcessingRunModel.tenant_id == tenant_id,
				EventProcessingRunModel.job_type == ProcessingJobType.SCORE_EVENT,
			)
		)
		(
			latest_analysis_at,
			latest_analysis_success_at,
			pending_analysis_count,
			failed_analysis_count,
		) = analysis_result.one()

		connection_result = await self._session.execute(
			select(func.count(TenantProviderConnectionModel.id)).where(
				TenantProviderConnectionModel.tenant_id == tenant_id,
				TenantProviderConnectionModel.status
				== TenantProviderConnectionStatus.ACTIVE,
			)
		)
		active_connection_count = connection_result.scalar_one()

		response_result = await self._session.execute(
			select(
				func.max(
					func.coalesce(
						EnforcementActionModel.completed_at,
						EnforcementActionModel.requested_at,
					)
				),
				func.max(EnforcementActionModel.completed_at).filter(
					EnforcementActionModel.status == EnforcementActionStatus.SUCCEEDED
				),
				func.count().filter(
					EnforcementActionModel.status.in_(
						(
							EnforcementActionStatus.PENDING,
							EnforcementActionStatus.SENT,
						)
					),
				),
				func.count().filter(
					and_(
						EnforcementActionModel.status == EnforcementActionStatus.FAILED,
						EnforcementActionModel.requested_at >= failure_since,
					)
				),
			).where(EnforcementActionModel.tenant_id == tenant_id)
		)
		(
			latest_response_at,
			latest_response_success_at,
			pending_response_count,
			failed_response_count,
		) = response_result.one()

		return [
			PipelineHealthRecord(
				component=PipelineComponent.INGESTION,
				configured_count=int(active_source_count),
				last_activity_at=latest_event_at,
				last_success_at=latest_event_at,
				pending_count=0,
				failed_count=0,
			),
			PipelineHealthRecord(
				component=PipelineComponent.ANALYSIS,
				configured_count=1,
				last_activity_at=latest_analysis_at,
				last_success_at=latest_analysis_success_at,
				pending_count=int(pending_analysis_count),
				failed_count=int(failed_analysis_count),
			),
			PipelineHealthRecord(
				component=PipelineComponent.RESPONSES,
				configured_count=int(active_connection_count),
				last_activity_at=latest_response_at,
				last_success_at=latest_response_success_at,
				pending_count=int(pending_response_count),
				failed_count=int(failed_response_count),
			),
		]

	async def get_activity_trends(
		self,
		tenant_id: UUID,
		filters: ActivityTrendFilterParams,
	) -> list[ActivityTrendBucketRecord]:
		"""Return zero-filled tenant activity trend buckets.

		Args:
			tenant_id: The owning tenant identifier.
		filters: The requested time range and bucket interval.

		Returns:
			Chronologically ordered activity buckets, including empty buckets.
		"""
		occurred_before = self._as_utc(filters.occurred_before or datetime.now(UTC))
		default_duration = (
			timedelta(hours=24)
			if filters.interval == ActivityTrendInterval.HOUR
			else timedelta(days=30)
		)
		occurred_after = self._as_utc(
			filters.occurred_after or occurred_before - default_duration
		)
		bucket_delta = self._bucket_delta(filters.interval)
		bucket_starts = self._bucket_starts(
			occurred_after,
			occurred_before,
			filters.interval,
		)
		buckets = {
			bucket_start: ActivityTrendBucketRecord(
				bucket_start=bucket_start,
				bucket_end=bucket_start + bucket_delta,
			)
			for bucket_start in bucket_starts
		}

		latest_scores = (
			select(
				RiskScoreModel.auth_event_id.label('auth_event_id'),
				RiskScoreModel.score_band.label('score_band'),
				func.row_number()
				.over(
					partition_by=RiskScoreModel.auth_event_id,
					order_by=RiskScoreModel.scored_at.desc(),
				)
				.label('row_number'),
			)
			.where(RiskScoreModel.tenant_id == tenant_id)
			.subquery()
		)
		event_bucket = func.date_trunc(
			filters.interval.value,
			AuthEventModel.occurred_at,
		).label('bucket_start')
		event_result = await self._session.execute(
			select(
				event_bucket,
				func.count(AuthEventModel.id),
				func.count().filter(latest_scores.c.score_band.is_not(None)),
				func.count().filter(latest_scores.c.score_band == ScoreBand.SAFE),
				func.count().filter(latest_scores.c.score_band == ScoreBand.CAUTION),
				func.count().filter(latest_scores.c.score_band == ScoreBand.LOCKOUT),
			)
			.select_from(AuthEventModel)
			.outerjoin(
				latest_scores,
				and_(
					latest_scores.c.auth_event_id == AuthEventModel.id,
					latest_scores.c.row_number == 1,
				),
			)
			.where(
				AuthEventModel.tenant_id == tenant_id,
				AuthEventModel.occurred_at >= occurred_after,
				AuthEventModel.occurred_at <= occurred_before,
			)
			.group_by(event_bucket)
		)
		for row in event_result.all():
			bucket = buckets.get(self._as_utc(row[0]))
			if bucket is None:
				continue
			bucket.event_count = int(row[1])
			bucket.scored_count = int(row[2])
			bucket.safe_count = int(row[3])
			bucket.caution_count = int(row[4])
			bucket.lockout_count = int(row[5])
			bucket.unscored_count = bucket.event_count - bucket.scored_count

		await self._merge_counts(
			buckets,
			PolicyDecisionModel,
			PolicyDecisionModel.decided_at,
			'decision_count',
			tenant_id,
			occurred_after,
			occurred_before,
			filters.interval,
		)
		await self._merge_counts(
			buckets,
			AlertModel,
			AlertModel.created_at,
			'alert_count',
			tenant_id,
			occurred_after,
			occurred_before,
			filters.interval,
		)
		await self._merge_counts(
			buckets,
			EnforcementActionModel,
			EnforcementActionModel.requested_at,
			'response_count',
			tenant_id,
			occurred_after,
			occurred_before,
			filters.interval,
		)

		return list(buckets.values())

	async def _merge_counts(
		self,
		buckets: dict[datetime, ActivityTrendBucketRecord],
		model: Any,
		timestamp_column: Any,
		field_name: str,
		tenant_id: UUID,
		occurred_after: datetime,
		occurred_before: datetime,
		interval: ActivityTrendInterval,
	) -> None:
		bucket_expression = func.date_trunc(interval.value, timestamp_column)
		result = await self._session.execute(
			select(bucket_expression, func.count())
			.select_from(model)
			.where(
				model.tenant_id == tenant_id,
				timestamp_column >= occurred_after,
				timestamp_column <= occurred_before,
			)
			.group_by(bucket_expression)
		)
		for bucket_start, count in result.all():
			bucket = buckets.get(self._as_utc(bucket_start))
			if bucket is not None:
				setattr(bucket, field_name, int(count))

	@staticmethod
	def _bucket_delta(interval: ActivityTrendInterval) -> timedelta:
		return (
			timedelta(hours=1)
			if interval == ActivityTrendInterval.HOUR
			else timedelta(days=1)
		)

	@classmethod
	def _bucket_starts(
		cls,
		occurred_after: datetime,
		occurred_before: datetime,
		interval: ActivityTrendInterval,
	) -> list[datetime]:
		bucket_delta = cls._bucket_delta(interval)
		cursor = occurred_after.replace(
			minute=0,
			second=0,
			microsecond=0,
		)
		if interval == ActivityTrendInterval.DAY:
			cursor = cursor.replace(hour=0)
		last_bucket = occurred_before.replace(
			minute=0,
			second=0,
			microsecond=0,
		)
		if interval == ActivityTrendInterval.DAY:
			last_bucket = last_bucket.replace(hour=0)

		starts: list[datetime] = []
		while cursor <= last_bucket:
			starts.append(cursor)
			cursor += bucket_delta
		return starts

	@staticmethod
	def _as_utc(value: datetime) -> datetime:
		if value.tzinfo is None:
			return value.replace(tzinfo=UTC)
		return value.astimezone(UTC)
