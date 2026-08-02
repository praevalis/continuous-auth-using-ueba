from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from schemas.tenant import (
	EventSourceCreateSchema,
	EventSourceFilterParams,
	EventSourceMetadataUpdateSchema,
	EventSourceSchema,
	IngestionCredentialCreateSchema,
	IngestionCredentialFilterParams,
	IngestionCredentialMetadataUpdateSchema,
	IngestionCredentialSchema,
	IssuedIngestionCredentialSchema,
)

from api.dependencies import (
	get_event_source_service,
	get_ingestion_credential_service,
)
from api.services.ingestion import (
	EventSourceService,
	IngestionCredentialService,
)

router = APIRouter(prefix='/ingestion', tags=['ingestion'])


@router.post(
	'/event-sources',
	response_model=EventSourceSchema,
	status_code=status.HTTP_201_CREATED,
)
async def create_event_source(
	tenant_id: Annotated[UUID, Query()],
	payload: EventSourceCreateSchema,
	service: Annotated[EventSourceService, Depends(get_event_source_service)],
) -> EventSourceSchema:
	"""Create an event source.

	Args:
		tenant_id: The owning tenant identifier.
		payload: The event source payload.
		service: The event source service.

	Returns:
		The created event source.
	"""
	return await service.create_event_source(tenant_id, payload)


@router.get('/event-sources', response_model=list[EventSourceSchema])
async def list_event_sources(
	tenant_id: Annotated[UUID, Query()],
	filters: Annotated[EventSourceFilterParams, Depends()],
	service: Annotated[EventSourceService, Depends(get_event_source_service)],
) -> list[EventSourceSchema]:
	"""Return event sources for a tenant.

	Args:
		tenant_id: The owning tenant identifier.
		filters: The event source filter parameters.
		service: The event source service.

	Returns:
		The event sources for the tenant.
	"""
	return await service.list_event_sources(tenant_id, filters)


@router.get('/event-sources/{event_source_id}', response_model=EventSourceSchema)
async def get_event_source(
	event_source_id: UUID,
	service: Annotated[EventSourceService, Depends(get_event_source_service)],
) -> EventSourceSchema:
	"""Return an event source by identifier.

	Args:
		event_source_id: The event source identifier.
		service: The event source service.

	Returns:
		The matching event source.
	"""
	return await service.get_event_source(event_source_id)


@router.patch('/event-sources/{event_source_id}', response_model=EventSourceSchema)
async def update_event_source(
	event_source_id: UUID,
	payload: EventSourceMetadataUpdateSchema,
	service: Annotated[EventSourceService, Depends(get_event_source_service)],
) -> EventSourceSchema:
	"""Update event source metadata by identifier.

	Args:
		event_source_id: The event source identifier.
		payload: The event source update payload.
		service: The event source service.

	Returns:
		The updated event source.
	"""
	return await service.update_event_source(event_source_id, payload)


@router.post(
	'/event-sources/{event_source_id}/activate', response_model=EventSourceSchema
)
async def activate_event_source(
	event_source_id: UUID,
	service: Annotated[EventSourceService, Depends(get_event_source_service)],
) -> EventSourceSchema:
	"""Activate a disabled event source.

	Args:
		event_source_id: The event source identifier.
		service: The event source service.

	Returns:
		The activated event source.
	"""
	return await service.activate_event_source(event_source_id)


@router.post(
	'/event-sources/{event_source_id}/disable', response_model=EventSourceSchema
)
async def disable_event_source(
	event_source_id: UUID,
	service: Annotated[EventSourceService, Depends(get_event_source_service)],
) -> EventSourceSchema:
	"""Disable an active event source.

	Args:
		event_source_id: The event source identifier.
		service: The event source service.

	Returns:
		The disabled event source.
	"""
	return await service.disable_event_source(event_source_id)


@router.delete(
	'/event-sources/{event_source_id}', status_code=status.HTTP_204_NO_CONTENT
)
async def delete_event_source(
	event_source_id: UUID,
	service: Annotated[EventSourceService, Depends(get_event_source_service)],
) -> Response:
	"""Delete an event source by identifier.

	Args:
		event_source_id: The event source identifier.
		service: The event source service.

	Returns:
		An empty response.
	"""
	await service.delete_event_source(event_source_id)
	return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
	'/ingestion-credentials',
	response_model=IssuedIngestionCredentialSchema,
	status_code=status.HTTP_201_CREATED,
)
async def issue_ingestion_credential(
	tenant_id: Annotated[UUID, Query()],
	payload: IngestionCredentialCreateSchema,
	service: Annotated[
		IngestionCredentialService,
		Depends(get_ingestion_credential_service),
	],
) -> IssuedIngestionCredentialSchema:
	"""Issue an ingestion credential.

	Args:
		tenant_id: The owning tenant identifier.
		payload: The ingestion credential payload.
		service: The ingestion credential service.

	Returns:
		The issued credential metadata and plaintext secret.
	"""
	return await service.issue_ingestion_credential(tenant_id, payload)


@router.get(
	'/ingestion-credentials',
	response_model=list[IngestionCredentialSchema],
)
async def list_ingestion_credentials(
	tenant_id: Annotated[UUID, Query()],
	filters: Annotated[IngestionCredentialFilterParams, Depends()],
	service: Annotated[
		IngestionCredentialService,
		Depends(get_ingestion_credential_service),
	],
) -> list[IngestionCredentialSchema]:
	"""Return ingestion credentials for a tenant.

	Args:
		tenant_id: The owning tenant identifier.
		filters: The ingestion credential filter parameters.
		service: The ingestion credential service.

	Returns:
		The ingestion credentials for the tenant.
	"""
	return await service.list_ingestion_credentials(tenant_id, filters)


@router.get(
	'/ingestion-credentials/{credential_id}',
	response_model=IngestionCredentialSchema,
)
async def get_ingestion_credential(
	credential_id: UUID,
	service: Annotated[
		IngestionCredentialService,
		Depends(get_ingestion_credential_service),
	],
) -> IngestionCredentialSchema:
	"""Return an ingestion credential by identifier.

	Args:
		credential_id: The ingestion credential identifier.
		service: The ingestion credential service.

	Returns:
		The matching ingestion credential.
	"""
	return await service.get_ingestion_credential(credential_id)


@router.patch(
	'/ingestion-credentials/{credential_id}',
	response_model=IngestionCredentialSchema,
)
async def update_ingestion_credential(
	credential_id: UUID,
	payload: IngestionCredentialMetadataUpdateSchema,
	service: Annotated[
		IngestionCredentialService,
		Depends(get_ingestion_credential_service),
	],
) -> IngestionCredentialSchema:
	"""Update ingestion credential metadata by identifier.

	Args:
		credential_id: The ingestion credential identifier.
		payload: The ingestion credential update payload.
		service: The ingestion credential service.

	Returns:
		The updated ingestion credential.
	"""
	return await service.update_ingestion_credential(credential_id, payload)


@router.post(
	'/ingestion-credentials/{credential_id}/revoke',
	response_model=IngestionCredentialSchema,
)
async def revoke_ingestion_credential(
	credential_id: UUID,
	service: Annotated[
		IngestionCredentialService,
		Depends(get_ingestion_credential_service),
	],
) -> IngestionCredentialSchema:
	"""Revoke an active ingestion credential.

	Args:
		credential_id: The ingestion credential identifier.
		service: The ingestion credential service.

	Returns:
		The revoked ingestion credential.
	"""
	return await service.revoke_ingestion_credential(credential_id)


@router.post(
	'/ingestion-credentials/{credential_id}/rotate',
	response_model=IssuedIngestionCredentialSchema,
)
async def rotate_ingestion_credential(
	credential_id: UUID,
	service: Annotated[
		IngestionCredentialService,
		Depends(get_ingestion_credential_service),
	],
) -> IssuedIngestionCredentialSchema:
	"""Rotate an active ingestion credential.

	Args:
		credential_id: The ingestion credential identifier.
		service: The ingestion credential service.

	Returns:
		The rotated credential metadata and plaintext secret.
	"""
	return await service.rotate_ingestion_credential(credential_id)


@router.delete(
	'/ingestion-credentials/{credential_id}',
	status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ingestion_credential(
	credential_id: UUID,
	service: Annotated[
		IngestionCredentialService,
		Depends(get_ingestion_credential_service),
	],
) -> Response:
	"""Delete an ingestion credential by identifier.

	Args:
		credential_id: The ingestion credential identifier.
		service: The ingestion credential service.

	Returns:
		An empty response.
	"""
	await service.delete_ingestion_credential(credential_id)
	return Response(status_code=status.HTTP_204_NO_CONTENT)
