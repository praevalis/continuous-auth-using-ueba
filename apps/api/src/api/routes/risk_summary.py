from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from schemas.scoring import RiskSummaryFilterParams, RiskSummarySchema

from api.dependencies import get_risk_summary_read_service
from api.services.risk_summary import RiskSummaryReadService

router = APIRouter(prefix='/tenants/{tenant_id}/risk-summary', tags=['risk-summary'])


@router.get('', response_model=RiskSummarySchema)
async def get_risk_summary(
	tenant_id: UUID,
	filters: Annotated[RiskSummaryFilterParams, Depends()],
	service: Annotated[RiskSummaryReadService, Depends(get_risk_summary_read_service)],
) -> RiskSummarySchema:
	"""Return tenant event and scored-risk summary indicators."""
	return await service.get_summary(tenant_id, filters)
