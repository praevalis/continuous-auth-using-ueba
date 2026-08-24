from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from schemas.scoring import ActivityTrendFilterParams, ActivityTrendSchema

from api.dependencies import get_activity_trend_read_service
from api.services.activity_trends import ActivityTrendReadService

router = APIRouter(
	prefix='/tenants/{tenant_id}/activity-trends',
	tags=['activity-trends'],
)


@router.get('', response_model=ActivityTrendSchema)
async def get_activity_trends(
	tenant_id: UUID,
	filters: Annotated[ActivityTrendFilterParams, Depends()],
	service: Annotated[
		ActivityTrendReadService, Depends(get_activity_trend_read_service)
	],
) -> ActivityTrendSchema:
	"""Return zero-filled activity trends for a tenant."""
	return await service.get_trends(tenant_id, filters)
