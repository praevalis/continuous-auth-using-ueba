from uuid import UUID

from database.repositories import PolicyDecisionRepository
from schemas.policy import PolicyDecisionFilterParams, PolicyDecisionSchema
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import OffsetPaginationSchema
from api.schemas import PolicyDecisionListResponseSchema


class PolicyDecisionReadService:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the policy-decision read service."""
		self._repository = PolicyDecisionRepository(session)

	async def list_policy_decisions(
		self,
		tenant_id: UUID,
		filters: PolicyDecisionFilterParams,
	) -> PolicyDecisionListResponseSchema:
		result = await self._repository.list_policy_decisions_for_tenant(
			tenant_id, filters
		)
		item_count = len(result.items)
		return PolicyDecisionListResponseSchema(
			items=[
				PolicyDecisionSchema.model_validate(policy_decision)
				for policy_decision in result.items
			],
			pagination=OffsetPaginationSchema(
				limit=filters.limit,
				offset=filters.offset,
				total_count=result.total_count,
				has_next=filters.offset + item_count < result.total_count,
				has_prev=filters.offset > 0,
			),
		)

	async def get_policy_decision(
		self,
		tenant_id: UUID,
		policy_decision_id: UUID,
	) -> PolicyDecisionSchema:
		policy_decision = (
			await self._repository.get_policy_decision_for_tenant_by_id_or_raise(
				tenant_id,
				policy_decision_id,
			)
		)
		return PolicyDecisionSchema.model_validate(policy_decision)
