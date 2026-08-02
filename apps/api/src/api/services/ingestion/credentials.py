import hashlib
import secrets
from datetime import UTC, datetime
from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import (
	EventSourceNotFoundError,
	InvalidIngestionCredentialStateError,
)
from domain.tenant import IngestionCredentialStatus
from schemas.tenant import (
	IngestionCredentialCreateSchema,
	IngestionCredentialFilterParams,
	IngestionCredentialMetadataUpdateSchema,
	IngestionCredentialSchema,
	IngestionCredentialUpdateSchema,
	IssuedIngestionCredentialSchema,
)


class IngestionCredentialService:
	def __init__(self, uow: IUnitOfWork) -> None:
		"""Initialize the ingestion credential service.

		Args:
			uow: The request-scoped database unit of work.
		"""
		self._uow = uow

	async def issue_ingestion_credential(
		self,
		tenant_id: UUID,
		payload: IngestionCredentialCreateSchema,
	) -> IssuedIngestionCredentialSchema:
		"""Issue an ingestion credential for a tenant.

		Args:
			tenant_id: The tenant identifier.
			payload: The ingestion credential payload.

		Returns:
			The persisted credential metadata and the plaintext secret.

		Raises:
			TenantNotFoundError: If the tenant does not exist.
			EventSourceNotFoundError: If the provided event source does not belong to
				the tenant.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)

		if payload.event_source_id is not None:
			event_source = await self._uow.event_sources.get_event_source_by_id(
				payload.event_source_id
			)
			if event_source is None or event_source.tenant_id != tenant_id:
				raise EventSourceNotFoundError(
					f'Event source "{payload.event_source_id}" does not exist for '
					f'tenant "{tenant_id}".'
				)

		plaintext_secret = f'ca_{secrets.token_urlsafe(32)}'
		credential_model = (
			await self._uow.ingestion_credentials.create_ingestion_credential(
				tenant_id,
				payload,
				key_id=f'ik_{secrets.token_hex(16)}',
				key_hash=hashlib.sha256(plaintext_secret.encode('utf-8')).hexdigest(),
				status=IngestionCredentialStatus.ACTIVE,
			)
		)
		await self._uow.commit()
		return IssuedIngestionCredentialSchema(
			credential=IngestionCredentialSchema.model_validate(credential_model),
			plaintext_secret=plaintext_secret,
		)

	async def list_ingestion_credentials(
		self,
		tenant_id: UUID,
		filters: IngestionCredentialFilterParams,
	) -> list[IngestionCredentialSchema]:
		"""Return ingestion credentials for a tenant.

		Args:
			tenant_id: The tenant identifier.
			filters: The ingestion credential filter parameters.

		Returns:
			The ingestion credential response schemas for the tenant.
		"""
		await self._uow.tenants.get_active_tenant_by_id_or_raise(tenant_id)
		credential_models = (
			await self._uow.ingestion_credentials.list_ingestion_credentials_for_tenant(
				tenant_id,
				filters,
			)
		)
		return [
			IngestionCredentialSchema.model_validate(credential_model)
			for credential_model in credential_models
		]

	async def get_ingestion_credential(
		self,
		credential_id: UUID,
	) -> IngestionCredentialSchema:
		"""Return an ingestion credential by identifier.

		Args:
			credential_id: The ingestion credential identifier.

		Returns:
			The matching ingestion credential response schema.
		"""
		credential_model = await self._uow.ingestion_credentials.get_ingestion_credential_by_id_or_raise(
			credential_id
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			credential_model.tenant_id
		)
		return IngestionCredentialSchema.model_validate(credential_model)

	async def update_ingestion_credential(
		self,
		credential_id: UUID,
		payload: IngestionCredentialMetadataUpdateSchema,
	) -> IngestionCredentialSchema:
		"""Update ingestion credential metadata by identifier.

		Args:
			credential_id: The ingestion credential identifier.
			payload: The ingestion credential metadata update payload.

		Returns:
			The updated ingestion credential response schema.
		"""
		credential_model = await self._uow.ingestion_credentials.get_ingestion_credential_by_id_or_raise(
			credential_id
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			credential_model.tenant_id
		)
		updated_credential_model = (
			await self._uow.ingestion_credentials.update_ingestion_credential(
				credential_id,
				IngestionCredentialUpdateSchema.model_validate(
					payload.model_dump(exclude_unset=True)
				),
			)
		)
		await self._uow.commit()
		return IngestionCredentialSchema.model_validate(updated_credential_model)

	async def revoke_ingestion_credential(
		self,
		credential_id: UUID,
	) -> IngestionCredentialSchema:
		"""Revoke an active ingestion credential.

		Args:
			credential_id: The ingestion credential identifier.

		Returns:
			The revoked ingestion credential response schema.
		"""
		credential_model = await self._uow.ingestion_credentials.get_ingestion_credential_by_id_or_raise(
			credential_id
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			credential_model.tenant_id
		)
		if credential_model.status == IngestionCredentialStatus.REVOKED:
			raise InvalidIngestionCredentialStateError(
				f'Ingestion credential "{credential_id}" is already revoked.'
			)
		if credential_model.status == IngestionCredentialStatus.EXPIRED:
			raise InvalidIngestionCredentialStateError(
				f'Expired ingestion credential "{credential_id}" cannot be revoked.'
			)

		updated_credential_model = (
			await self._uow.ingestion_credentials.update_ingestion_credential(
				credential_id,
				IngestionCredentialUpdateSchema(
					status=IngestionCredentialStatus.REVOKED,
				),
			)
		)
		await self._uow.commit()
		return IngestionCredentialSchema.model_validate(updated_credential_model)

	async def rotate_ingestion_credential(
		self,
		credential_id: UUID,
	) -> IssuedIngestionCredentialSchema:
		"""Rotate an active ingestion credential.

		Args:
			credential_id: The ingestion credential identifier.

		Returns:
			The rotated credential metadata and the new plaintext secret.
		"""
		credential_model = await self._uow.ingestion_credentials.get_ingestion_credential_by_id_or_raise(
			credential_id
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			credential_model.tenant_id
		)
		if credential_model.status != IngestionCredentialStatus.ACTIVE:
			raise InvalidIngestionCredentialStateError(
				'Only active ingestion credentials can be rotated.'
			)

		plaintext_secret = f'ca_{secrets.token_urlsafe(32)}'
		updated_credential_model = (
			await self._uow.ingestion_credentials.update_ingestion_credential(
				credential_id,
				IngestionCredentialUpdateSchema(
					key_id=f'ik_{secrets.token_hex(16)}',
					key_hash=hashlib.sha256(
						plaintext_secret.encode('utf-8')
					).hexdigest(),
					rotated_at=datetime.now(UTC),
					status=IngestionCredentialStatus.ACTIVE,
				),
			)
		)
		await self._uow.commit()
		return IssuedIngestionCredentialSchema(
			credential=IngestionCredentialSchema.model_validate(
				updated_credential_model
			),
			plaintext_secret=plaintext_secret,
		)

	async def delete_ingestion_credential(self, credential_id: UUID) -> None:
		"""Delete an ingestion credential by identifier.

		Args:
			credential_id: The ingestion credential identifier.
		"""
		credential_model = await self._uow.ingestion_credentials.get_ingestion_credential_by_id_or_raise(
			credential_id
		)
		await self._uow.tenants.get_active_tenant_by_id_or_raise(
			credential_model.tenant_id
		)
		await self._uow.ingestion_credentials.delete_ingestion_credential(credential_id)
		await self._uow.commit()
