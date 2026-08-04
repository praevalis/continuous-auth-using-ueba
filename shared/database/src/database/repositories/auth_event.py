from uuid import UUID

from domain.exceptions import AuthEventNotFoundError
from schemas.event import AuthEventCreateSchema
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import AuthEventModel


class AuthEventRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the auth-event repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_auth_event(
		self,
		payload: AuthEventCreateSchema,
	) -> AuthEventModel:
		"""Persist a canonical authentication event.

		Args:
			payload: The normalized and anonymized auth-event payload.

		Returns:
			The persisted auth-event model.
		"""
		auth_event = AuthEventModel(**payload.model_dump())
		self._session.add(auth_event)
		await self._session.flush()
		await self._session.refresh(auth_event)
		return auth_event

	async def create_auth_events(
		self,
		payloads: list[AuthEventCreateSchema],
	) -> list[tuple[UUID, UUID]]:
		"""Persist canonical authentication events in a batch.

		Args:
			payloads: The normalized and anonymized auth-event payloads.

		Returns:
			The newly created auth-event identifiers paired with tenant
			identifiers.
		"""
		if not payloads:
			return []

		statement = (
			insert(AuthEventModel)
			.values([payload.model_dump(mode='python') for payload in payloads])
			.on_conflict_do_nothing(index_elements=['tenant_id', 'idempotency_key'])
			.returning(AuthEventModel.id, AuthEventModel.tenant_id)
		)
		result = await self._session.execute(statement)
		return [(row.id, row.tenant_id) for row in result.all()]

	async def get_auth_event_by_id(
		self,
		auth_event_id: UUID,
	) -> AuthEventModel | None:
		"""Return an auth event by identifier, if present.

		Args:
			auth_event_id: The auth event identifier to resolve.

		Returns:
			The matching auth event model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(AuthEventModel).where(AuthEventModel.id == auth_event_id)
		)
		return result.scalar_one_or_none()

	async def get_auth_event_by_id_or_raise(
		self,
		auth_event_id: UUID,
	) -> AuthEventModel:
		"""Return an auth event by identifier or raise if it is missing.

		Args:
			auth_event_id: The auth event identifier to resolve.

		Returns:
			The matching auth event model.

		Raises:
			AuthEventNotFoundError: If the auth event does not exist.
		"""
		auth_event = await self.get_auth_event_by_id(auth_event_id)
		if auth_event is None:
			raise AuthEventNotFoundError(
				f'Auth event "{auth_event_id}" does not exist.'
			)

		return auth_event
