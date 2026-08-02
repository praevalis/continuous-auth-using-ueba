from schemas.event import AuthEventCreateSchema
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
	) -> int:
		"""Persist canonical authentication events in a batch.

		Args:
			payloads: The normalized and anonymized auth-event payloads.

		Returns:
			The number of persisted auth events.
		"""
		auth_events = [AuthEventModel(**payload.model_dump()) for payload in payloads]
		self._session.add_all(auth_events)
		await self._session.flush()
		return len(auth_events)
