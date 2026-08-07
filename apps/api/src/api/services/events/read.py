from uuid import UUID

from database.repositories import AuthEventRepository
from schemas.event import AuthEventListFilterParams, AuthEventSchema
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import OffsetPaginationSchema
from api.schemas import AuthEventListResponseSchema


class AuthEventReadService:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the auth-event read service."""
		self._repository = AuthEventRepository(session)

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
	) -> AuthEventSchema:
		event = await self._repository.get_auth_event_for_tenant_by_id_or_raise(
			tenant_id, auth_event_id
		)
		return AuthEventSchema.model_validate(event)
