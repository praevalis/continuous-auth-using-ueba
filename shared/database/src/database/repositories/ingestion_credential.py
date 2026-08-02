from uuid import UUID

from domain.exceptions import (
	EventSourceNotFoundError,
	IngestionCredentialAlreadyExistsError,
	IngestionCredentialNotFoundError,
)
from schemas.tenant import (
	IngestionCredentialCreateSchema,
	IngestionCredentialFilterParams,
	IngestionCredentialUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import IngestionCredentialModel
from database.repositories.event_source import EventSourceRepository


class IngestionCredentialRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the ingestion credential repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session
		self._event_source_repository = EventSourceRepository(session)

	async def create_ingestion_credential(
		self,
		tenant_id: UUID,
		payload: IngestionCredentialCreateSchema,
		*,
		key_id: str,
		key_hash: str,
		status: str,
	) -> IngestionCredentialModel:
		"""Persist an ingestion credential.

		Args:
			tenant_id: The owning tenant identifier.
			payload: The credential creation payload.
			key_id: The generated public credential identifier.
			key_hash: The hashed secret value.
			status: The initial persisted credential status.

		Returns:
			The persisted ingestion credential model.
		"""
		credential = IngestionCredentialModel(
			tenant_id=tenant_id,
			key_id=key_id,
			key_hash=key_hash,
			status=status,
			last_used_at=None,
			rotated_at=None,
			**payload.model_dump(),
		)
		self._session.add(credential)
		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(
				error,
				'uq_ingestion_credentials_key_id',
				'ingestion_credentials_key_id_key',
			):
				raise IngestionCredentialAlreadyExistsError(
					'An ingestion credential with the generated key identifier '
					'already exists.'
				) from error
			raise

		await self._session.refresh(credential)
		return credential

	async def update_ingestion_credential(
		self,
		credential_id: UUID,
		payload: IngestionCredentialUpdateSchema,
	) -> IngestionCredentialModel:
		"""Persist updates to an ingestion credential.

		Args:
			credential_id: The ingestion credential identifier to update.
			payload: The ingestion credential update payload.

		Returns:
			The updated ingestion credential model.

		Raises:
			IngestionCredentialNotFoundError: If the credential does not exist.
			EventSourceNotFoundError: If the provided event source does not belong to
				the same tenant as the credential.
		"""
		credential = await self.get_ingestion_credential_by_id_or_raise(credential_id)

		if payload.event_source_id is not None:
			event_source = await self._event_source_repository.get_event_source_by_id(
				payload.event_source_id
			)
			if event_source is None or event_source.tenant_id != credential.tenant_id:
				raise EventSourceNotFoundError(
					f'Event source "{payload.event_source_id}" does not exist for '
					f'tenant "{credential.tenant_id}".'
				)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(credential, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(credential)
		return credential

	async def delete_ingestion_credential(
		self,
		credential_id: UUID,
	) -> None:
		"""Delete an ingestion credential by identifier.

		Args:
			credential_id: The ingestion credential identifier to delete.

		Raises:
			IngestionCredentialNotFoundError: If the credential does not exist.
		"""
		credential = await self.get_ingestion_credential_by_id_or_raise(credential_id)
		await self._session.delete(credential)
		await self._session.flush()

	async def list_ingestion_credentials_for_tenant(
		self,
		tenant_id: UUID,
		filters: IngestionCredentialFilterParams,
	) -> list[IngestionCredentialModel]:
		"""Return all ingestion credentials for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Ingestion credential filter parameters.

		Returns:
			The ingestion credential models associated with the tenant.
		"""
		statement = select(IngestionCredentialModel).where(
			IngestionCredentialModel.tenant_id == tenant_id
		)
		if filters.event_source_id is not None:
			statement = statement.where(
				IngestionCredentialModel.event_source_id == filters.event_source_id
			)
		if filters.credential_type is not None:
			statement = statement.where(
				IngestionCredentialModel.credential_type == filters.credential_type
			)
		if filters.status is not None:
			statement = statement.where(
				IngestionCredentialModel.status == filters.status
			)

		result = await self._session.execute(statement)
		return list(result.scalars().all())

	async def get_ingestion_credential_by_id(
		self,
		credential_id: UUID,
	) -> IngestionCredentialModel | None:
		"""Return an ingestion credential by identifier, if present.

		Args:
			credential_id: The ingestion credential identifier to resolve.

		Returns:
			The matching ingestion credential model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(IngestionCredentialModel).where(
				IngestionCredentialModel.id == credential_id
			)
		)
		return result.scalar_one_or_none()

	async def get_ingestion_credential_by_id_or_raise(
		self,
		credential_id: UUID,
	) -> IngestionCredentialModel:
		"""Return an ingestion credential by identifier or raise if it is missing.

		Args:
			credential_id: The ingestion credential identifier to resolve.

		Returns:
			The matching ingestion credential model.

		Raises:
			IngestionCredentialNotFoundError: If the credential does not exist.
		"""
		credential = await self.get_ingestion_credential_by_id(credential_id)
		if credential is None:
			raise IngestionCredentialNotFoundError(
				f'Ingestion credential "{credential_id}" does not exist.'
			)

		return credential

	@staticmethod
	def _matches_constraint(error: IntegrityError, *constraint_names: str) -> bool:
		"""Return whether an integrity error references one of the given constraints.

		Args:
			error: The raised SQLAlchemy integrity error.
			*constraint_names: Known database constraint names to match.

		Returns:
			True when the error references one of the provided constraint names.
		"""
		error_message = str(error.orig)
		return any(
			constraint_name in error_message for constraint_name in constraint_names
		)
