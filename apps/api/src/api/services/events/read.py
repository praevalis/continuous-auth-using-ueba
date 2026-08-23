from uuid import UUID

from database.queries import ThreatFeedQueryService
from database.repositories import AuthEventRepository
from schemas.alert import AlertSchema
from schemas.enforcement import EnforcementActionSchema
from schemas.event import (
	AuthEventDetailSchema,
	AuthEventListFilterParams,
	AuthEventSchema,
)
from schemas.policy import PolicyDecisionSchema
from schemas.scoring import (
	EventProcessingRunSchema,
	FeatureSnapshotSchema,
	RiskScoreSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import OffsetPaginationSchema
from api.schemas import AuthEventListResponseSchema


class AuthEventReadService:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the auth-event read service."""
		self._repository = AuthEventRepository(session)
		self._query_service = ThreatFeedQueryService(session)

	async def list_events(
		self,
		tenant_id: UUID,
		filters: AuthEventListFilterParams,
	) -> AuthEventListResponseSchema:
		result = await self._repository.list_auth_events_for_tenant(tenant_id, filters)
		item_count = len(result.items)
		return AuthEventListResponseSchema(
			items=[AuthEventSchema.model_validate(event) for event in result.items],
			pagination=OffsetPaginationSchema(
				limit=filters.limit,
				offset=filters.offset,
				total_count=result.total_count,
				has_next=filters.offset + item_count < result.total_count,
				has_prev=filters.offset > 0,
			),
		)

	async def get_event(
		self,
		tenant_id: UUID,
		auth_event_id: UUID,
	) -> AuthEventDetailSchema:
		"""Return an event with its processing and response evidence.

		Args:
			tenant_id: The owning tenant identifier.
			auth_event_id: The authentication event identifier to resolve.

		Returns:
			The event detail aggregate containing the latest scoring, policy,
			alert, and enforcement records.

		Raises:
			AuthEventNotFoundError: If the event does not exist for the tenant.
		"""
		detail = await self._query_service.get_event_detail_for_tenant(
			tenant_id, auth_event_id
		)
		return AuthEventDetailSchema(
			event=AuthEventSchema.model_validate(detail.event),
			processing_run=(
				None
				if detail.processing_run is None
				else EventProcessingRunSchema.model_validate(detail.processing_run)
			),
			feature_snapshot=(
				None
				if detail.feature_snapshot is None
				else FeatureSnapshotSchema.model_validate(detail.feature_snapshot)
			),
			risk_score=(
				None
				if detail.risk_score is None
				else RiskScoreSchema.model_validate(detail.risk_score)
			),
			policy_decision=(
				None
				if detail.policy_decision is None
				else PolicyDecisionSchema.model_validate(detail.policy_decision)
			),
			alerts=[AlertSchema.model_validate(alert) for alert in detail.alerts],
			enforcement_actions=[
				EnforcementActionSchema.model_validate(action)
				for action in detail.enforcement_actions
			],
		)
