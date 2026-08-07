from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from schemas.alert import AlertFilterParams, AlertSchema

from api.dependencies import get_alert_read_service
from api.schemas import AlertListResponseSchema
from api.services.alerts import AlertReadService

router = APIRouter(prefix='/tenants/{tenant_id}/alerts', tags=['alerts'])


@router.get('', response_model=AlertListResponseSchema)
async def list_alerts(
	tenant_id: UUID,
	filters: Annotated[AlertFilterParams, Depends()],
	service: Annotated[AlertReadService, Depends(get_alert_read_service)],
) -> AlertListResponseSchema:
	"""Return tenant alerts."""
	return await service.list_alerts(tenant_id, filters)


@router.get('/{alert_id}', response_model=AlertSchema)
async def get_alert(
	tenant_id: UUID,
	alert_id: UUID,
	service: Annotated[AlertReadService, Depends(get_alert_read_service)],
) -> AlertSchema:
	"""Return a tenant alert."""
	return await service.get_alert(tenant_id, alert_id)
