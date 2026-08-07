from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from schemas.policy import PolicyDecisionFilterParams, PolicyDecisionSchema

from api.dependencies import get_policy_decision_read_service
from api.schemas import PolicyDecisionListResponseSchema
from api.services.policy_decisions import PolicyDecisionReadService

router = APIRouter(
	prefix='/tenants/{tenant_id}/policy-decisions',
	tags=['policy-decisions'],
)


@router.get('', response_model=PolicyDecisionListResponseSchema)
async def list_policy_decisions(
	tenant_id: UUID,
	filters: Annotated[PolicyDecisionFilterParams, Depends()],
	service: Annotated[
		PolicyDecisionReadService, Depends(get_policy_decision_read_service)
	],
) -> PolicyDecisionListResponseSchema:
	"""Return tenant policy decisions."""
	return await service.list_policy_decisions(tenant_id, filters)


@router.get('/{policy_decision_id}', response_model=PolicyDecisionSchema)
async def get_policy_decision(
	tenant_id: UUID,
	policy_decision_id: UUID,
	service: Annotated[
		PolicyDecisionReadService, Depends(get_policy_decision_read_service)
	],
) -> PolicyDecisionSchema:
	"""Return a tenant policy decision."""
	return await service.get_policy_decision(tenant_id, policy_decision_id)
