from uuid import UUID

from database.repositories import AlertRepository
from schemas.alert import AlertFilterParams, AlertSchema
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import OffsetPaginationSchema
from api.schemas import AlertListResponseSchema


class AlertReadService:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the alert read service."""
		self._repository = AlertRepository(session)

	async def list_alerts(
		self,
		tenant_id: UUID,
		filters: AlertFilterParams,
	) -> AlertListResponseSchema:
		result = await self._repository.list_alerts_for_tenant(tenant_id, filters)
		item_count = len(result.items)
		return AlertListResponseSchema(
			items=[AlertSchema.model_validate(alert) for alert in result.items],
			pagination=OffsetPaginationSchema(
				limit=filters.limit,
				offset=filters.offset,
				total_count=result.total_count,
				has_next=filters.offset + item_count < result.total_count,
				has_prev=filters.offset > 0,
			),
		)

	async def get_alert(
		self,
		tenant_id: UUID,
		alert_id: UUID,
	) -> AlertSchema:
		alert = await self._repository.get_alert_for_tenant_by_id_or_raise(
			tenant_id,
			alert_id,
		)
		return AlertSchema.model_validate(alert)
