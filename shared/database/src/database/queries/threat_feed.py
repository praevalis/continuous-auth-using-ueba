from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.exceptions import AuthEventNotFoundError
from domain.policy import ScoreBand
from schemas.scoring import RiskSummaryFilterParams
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
	AlertModel,
	AuthEventModel,
	EnforcementActionModel,
	EventProcessingRunModel,
	FeatureSnapshotModel,
	PolicyDecisionModel,
	RiskScoreModel,
)


@dataclass(slots=True)
class AuthEventDetailRecord:
	"""Persisted records associated with one authentication event."""

	event: AuthEventModel
	processing_run: EventProcessingRunModel | None
	feature_snapshot: FeatureSnapshotModel | None
	risk_score: RiskScoreModel | None
	policy_decision: PolicyDecisionModel | None
	alerts: list[AlertModel]
	enforcement_actions: list[EnforcementActionModel]


class ThreatFeedQueryService:
	"""Read queries for event evidence and tenant risk indicators."""

	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the Threat Feed query service.

		Args:
			session: The async SQLAlchemy session backing the read queries.
		"""
		self._session = session

	async def get_event_detail_for_tenant(
		self,
		tenant_id: UUID,
		auth_event_id: UUID,
	) -> AuthEventDetailRecord:
		"""Return an event and its latest processing evidence.

		Args:
			tenant_id: The owning tenant identifier.
			auth_event_id: The authentication event identifier to resolve.

		Returns:
			The event with its latest processing, scoring, policy, alert, and
			enforcement records.

		Raises:
			AuthEventNotFoundError: If the event does not exist for the tenant.
		"""
		result = await self._session.execute(
			select(AuthEventModel).where(
				AuthEventModel.tenant_id == tenant_id,
				AuthEventModel.id == auth_event_id,
			)
		)
		event = result.scalar_one_or_none()
		if event is None:
			raise AuthEventNotFoundError(
				f'Auth event "{auth_event_id}" does not exist.'
			)

		processing_run = await self._latest_processing_run(tenant_id, auth_event_id)
		feature_snapshot = await self._latest_feature_snapshot(
			tenant_id,
			auth_event_id,
			processing_run.id if processing_run is not None else None,
		)

		risk_score = await self._latest_risk_score(tenant_id, auth_event_id)
		if risk_score is not None and (
			feature_snapshot is None
			or feature_snapshot.id != risk_score.feature_snapshot_id
		):
			feature_snapshot = await self._feature_snapshot_by_id(
				tenant_id, risk_score.feature_snapshot_id
			)

		policy_decision = await self._latest_policy_decision(tenant_id, auth_event_id)
		alerts: list[AlertModel] = []
		enforcement_actions: list[EnforcementActionModel] = []
		if policy_decision is not None:
			alerts = await self._alerts_for_policy_decision(
				tenant_id, policy_decision.id
			)
			enforcement_actions = await self._enforcement_actions_for_policy_decision(
				tenant_id, policy_decision.id
			)

		return AuthEventDetailRecord(
			event=event,
			processing_run=processing_run,
			feature_snapshot=feature_snapshot,
			risk_score=risk_score,
			policy_decision=policy_decision,
			alerts=alerts,
			enforcement_actions=enforcement_actions,
		)

	async def get_risk_summary(
		self,
		tenant_id: UUID,
		filters: RiskSummaryFilterParams,
	) -> tuple[int, dict[ScoreBand, int], datetime | None, datetime | None]:
		"""Return tenant event counts and scored-risk freshness.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Optional occurrence-time bounds for the summary.

		Returns:
			A tuple containing the event count, counts by score band, latest event
			timestamp, and latest score timestamp.
		"""
		event_filters = [AuthEventModel.tenant_id == tenant_id]

		if filters.occurred_after is not None:
			event_filters.append(AuthEventModel.occurred_at >= filters.occurred_after)

		if filters.occurred_before is not None:
			event_filters.append(AuthEventModel.occurred_at <= filters.occurred_before)

		event_result = await self._session.execute(
			select(
				func.count(AuthEventModel.id), func.max(AuthEventModel.occurred_at)
			).where(*event_filters)
		)
		event_count, latest_event_at = event_result.one()

		score_result = await self._session.execute(
			select(
				RiskScoreModel.score_band,
				func.count(func.distinct(RiskScoreModel.auth_event_id)),
				func.max(RiskScoreModel.scored_at),
			)
			.join(
				AuthEventModel,
				AuthEventModel.id == RiskScoreModel.auth_event_id,
			)
			.where(*event_filters)
			.group_by(RiskScoreModel.score_band)
		)
		band_counts: dict[ScoreBand, int] = {}
		latest_scored_at: datetime | None = None

		for band, count, scored_at in score_result.all():
			band_counts[band] = count

			if latest_scored_at is None or (
				scored_at is not None and scored_at > latest_scored_at
			):
				latest_scored_at = scored_at

		return int(event_count), band_counts, latest_event_at, latest_scored_at

	async def _latest_processing_run(
		self, tenant_id: UUID, auth_event_id: UUID
	) -> EventProcessingRunModel | None:
		"""Return the latest processing run for an event.

		Args:
			tenant_id: The owning tenant identifier.
			auth_event_id: The authentication event identifier.

		Returns:
			The most recently created processing run, or ``None`` when scoring has
			not started.
		"""
		result = await self._session.execute(
			select(EventProcessingRunModel)
			.where(
				EventProcessingRunModel.tenant_id == tenant_id,
				EventProcessingRunModel.auth_event_id == auth_event_id,
			)
			.order_by(EventProcessingRunModel.created_at.desc())
			.limit(1)
		)
		return result.scalar_one_or_none()

	async def _latest_feature_snapshot(
		self,
		tenant_id: UUID,
		auth_event_id: UUID,
		processing_run_id: UUID | None,
	) -> FeatureSnapshotModel | None:
		"""Return the latest feature snapshot for an event and run.

		Args:
			tenant_id: The owning tenant identifier.
			auth_event_id: The authentication event identifier.
			processing_run_id: The related processing run, when available.

		Returns:
			The latest computed feature snapshot, or ``None`` when no snapshot
			exists.
		"""
		statement = select(FeatureSnapshotModel).where(
			FeatureSnapshotModel.tenant_id == tenant_id,
			FeatureSnapshotModel.auth_event_id == auth_event_id,
		)
		if processing_run_id is not None:
			statement = statement.where(
				FeatureSnapshotModel.processing_run_id == processing_run_id
			)
		result = await self._session.execute(
			statement.order_by(FeatureSnapshotModel.computed_at.desc()).limit(1)
		)
		return result.scalar_one_or_none()

	async def _feature_snapshot_by_id(
		self, tenant_id: UUID, feature_snapshot_id: UUID
	) -> FeatureSnapshotModel | None:
		"""Return a tenant-scoped feature snapshot by identifier.

		Args:
			tenant_id: The owning tenant identifier.
			feature_snapshot_id: The feature snapshot identifier.

		Returns:
			The matching feature snapshot, or ``None`` when it is not found.
		"""
		result = await self._session.execute(
			select(FeatureSnapshotModel).where(
				FeatureSnapshotModel.tenant_id == tenant_id,
				FeatureSnapshotModel.id == feature_snapshot_id,
			)
		)
		return result.scalar_one_or_none()

	async def _latest_risk_score(
		self, tenant_id: UUID, auth_event_id: UUID
	) -> RiskScoreModel | None:
		"""Return the latest risk score for an event.

		Args:
			tenant_id: The owning tenant identifier.
			auth_event_id: The authentication event identifier.

		Returns:
			The most recently scored risk record, or ``None`` when scoring has not
			completed.
		"""
		result = await self._session.execute(
			select(RiskScoreModel)
			.where(
				RiskScoreModel.tenant_id == tenant_id,
				RiskScoreModel.auth_event_id == auth_event_id,
			)
			.order_by(RiskScoreModel.scored_at.desc())
			.limit(1)
		)
		return result.scalar_one_or_none()

	async def _latest_policy_decision(
		self, tenant_id: UUID, auth_event_id: UUID
	) -> PolicyDecisionModel | None:
		"""Return the latest policy decision for an event.

		Args:
			tenant_id: The owning tenant identifier.
			auth_event_id: The authentication event identifier.

		Returns:
			The most recently decided policy record, or ``None`` when policy
			evaluation has not completed.
		"""
		result = await self._session.execute(
			select(PolicyDecisionModel)
			.where(
				PolicyDecisionModel.tenant_id == tenant_id,
				PolicyDecisionModel.auth_event_id == auth_event_id,
			)
			.order_by(PolicyDecisionModel.decided_at.desc())
			.limit(1)
		)
		return result.scalar_one_or_none()

	async def _alerts_for_policy_decision(
		self, tenant_id: UUID, policy_decision_id: UUID
	) -> list[AlertModel]:
		"""Return alerts associated with a tenant policy decision.

		Args:
			tenant_id: The owning tenant identifier.
			policy_decision_id: The policy decision identifier.

		Returns:
			Alerts ordered from oldest to newest creation time.
		"""
		result = await self._session.execute(
			select(AlertModel)
			.where(
				AlertModel.tenant_id == tenant_id,
				AlertModel.policy_decision_id == policy_decision_id,
			)
			.order_by(AlertModel.created_at.asc())
		)
		return list(result.scalars().all())

	async def _enforcement_actions_for_policy_decision(
		self, tenant_id: UUID, policy_decision_id: UUID
	) -> list[EnforcementActionModel]:
		"""Return enforcement actions associated with a policy decision.

		Args:
			tenant_id: The owning tenant identifier.
			policy_decision_id: The policy decision identifier.

		Returns:
			Enforcement actions ordered from oldest to newest request time.
		"""
		result = await self._session.execute(
			select(EnforcementActionModel)
			.where(
				EnforcementActionModel.tenant_id == tenant_id,
				EnforcementActionModel.policy_decision_id == policy_decision_id,
			)
			.order_by(EnforcementActionModel.requested_at.asc())
		)
		return list(result.scalars().all())
