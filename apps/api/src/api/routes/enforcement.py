from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from schemas.enforcement import EnforcementActionFilterParams, EnforcementActionSchema

from api.dependencies import get_enforcement_read_service
from api.schemas import EnforcementActionListResponseSchema
from api.services.enforcement import EnforcementReadService

router = APIRouter(
	prefix='/tenants/{tenant_id}/enforcement-actions',
	tags=['enforcement'],
)


@router.get('', response_model=EnforcementActionListResponseSchema)
async def list_enforcement_actions(
	tenant_id: UUID,
	filters: Annotated[EnforcementActionFilterParams, Depends()],
	service: Annotated[EnforcementReadService, Depends(get_enforcement_read_service)],
) -> EnforcementActionListResponseSchema:
	"""Return tenant enforcement actions."""
	return await service.list_enforcement_actions(tenant_id, filters)


@router.get('/{enforcement_action_id}', response_model=EnforcementActionSchema)
async def get_enforcement_action(
	tenant_id: UUID,
	enforcement_action_id: UUID,
	service: Annotated[EnforcementReadService, Depends(get_enforcement_read_service)],
) -> EnforcementActionSchema:
	"""Return a tenant enforcement action."""
	return await service.get_enforcement_action(tenant_id, enforcement_action_id)
