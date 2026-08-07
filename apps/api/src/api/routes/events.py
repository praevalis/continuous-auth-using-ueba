from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from schemas.event import AuthEventListFilterParams, AuthEventSchema

from api.dependencies import get_auth_event_read_service
from api.schemas import AuthEventListResponseSchema
from api.services.events import AuthEventReadService

router = APIRouter(prefix='/tenants/{tenant_id}/events', tags=['events'])


@router.get('', response_model=AuthEventListResponseSchema)
async def list_events(
	tenant_id: UUID,
	filters: Annotated[AuthEventListFilterParams, Depends()],
	service: Annotated[AuthEventReadService, Depends(get_auth_event_read_service)],
) -> AuthEventListResponseSchema:
	"""Return tenant auth events."""
	return await service.list_events(tenant_id, filters)


@router.get('/{auth_event_id}', response_model=AuthEventSchema)
async def get_event(
	tenant_id: UUID,
	auth_event_id: UUID,
	service: Annotated[AuthEventReadService, Depends(get_auth_event_read_service)],
) -> AuthEventSchema:
	"""Return a tenant auth event."""
	return await service.get_event(tenant_id, auth_event_id)
