from uuid import UUID

from schemas.event import AuthEventCreateSchema
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
