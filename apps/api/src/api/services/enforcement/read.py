from uuid import UUID

from database.repositories import EnforcementActionRepository
from schemas.enforcement import EnforcementActionFilterParams, EnforcementActionSchema
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import OffsetPaginationSchema
from api.schemas import EnforcementActionListResponseSchema


class EnforcementReadService:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the enforcement read service."""
		self._repository = EnforcementActionRepository(session)

	async def list_enforcement_actions(
		self,
		tenant_id: UUID,
		filters: EnforcementActionFilterParams,
	) -> EnforcementActionListResponseSchema:
		result = await self._repository.list_enforcement_actions_for_tenant(
			tenant_id, filters
		)
		item_count = len(result.items)
		return EnforcementActionListResponseSchema(
			items=[
				EnforcementActionSchema.model_validate(enforcement_action)
				for enforcement_action in result.items
			],
			pagination=OffsetPaginationSchema(
				limit=filters.limit,
				offset=filters.offset,
				total_count=result.total_count,
				has_next=filters.offset + item_count < result.total_count,
				has_prev=filters.offset > 0,
			),
		)

	async def get_enforcement_action(
		self,
		tenant_id: UUID,
		enforcement_action_id: UUID,
	) -> EnforcementActionSchema:
		enforcement_action = (
			await self._repository.get_enforcement_action_for_tenant_by_id_or_raise(
				tenant_id,
				enforcement_action_id,
			)
		)
		return EnforcementActionSchema.model_validate(enforcement_action)
