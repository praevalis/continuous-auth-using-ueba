from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from schemas.tenant import PipelineHealthSchema

from api.dependencies import get_pipeline_health_read_service
from api.services.pipeline_health import PipelineHealthReadService

router = APIRouter(
	prefix='/tenants/{tenant_id}/pipeline-health',
	tags=['pipeline-health'],
)


@router.get('', response_model=PipelineHealthSchema)
async def get_pipeline_health(
	tenant_id: UUID,
	service: Annotated[
		PipelineHealthReadService, Depends(get_pipeline_health_read_service)
	],
) -> PipelineHealthSchema:
	"""Return computed pipeline health for a tenant."""
	return await service.get_health(tenant_id)
