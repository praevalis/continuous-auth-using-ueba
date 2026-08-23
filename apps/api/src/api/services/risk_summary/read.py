from datetime import UTC, datetime
from uuid import UUID

from database.queries import ThreatFeedQueryService
from domain.policy import ScoreBand
from schemas.scoring import RiskSummaryFilterParams, RiskSummarySchema
from sqlalchemy.ext.asyncio import AsyncSession


class RiskSummaryReadService:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the tenant risk-summary read service.

		Args:
			session: The async SQLAlchemy session backing the read queries.
		"""
		self._query_service = ThreatFeedQueryService(session)

	async def get_summary(
		self,
		tenant_id: UUID,
		filters: RiskSummaryFilterParams,
	) -> RiskSummarySchema:
		"""Return event and scored-risk indicators for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Optional occurrence-time bounds for the summary.

		Returns:
			The tenant risk summary with event counts and freshness timestamps.
		"""
		(
			event_count,
			band_counts,
			latest_event_at,
			latest_scored_at,
		) = await self._query_service.get_risk_summary(tenant_id, filters)
		scored_count = sum(band_counts.values())
		return RiskSummarySchema(
			tenant_id=tenant_id,
			occurred_after=filters.occurred_after,
			occurred_before=filters.occurred_before,
			event_count=event_count,
			safe_count=band_counts.get(ScoreBand.SAFE, 0),
			caution_count=band_counts.get(ScoreBand.CAUTION, 0),
			lockout_count=band_counts.get(ScoreBand.LOCKOUT, 0),
			unscored_count=max(event_count - scored_count, 0),
			latest_event_at=latest_event_at,
			latest_scored_at=latest_scored_at,
			generated_at=datetime.now(UTC),
		)
