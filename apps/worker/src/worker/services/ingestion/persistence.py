from database import IUnitOfWork
from schemas.event import AuthEventCreateSchema, AuthEventSchema


class AuthEventPersistenceService:
	def __init__(self, uow: IUnitOfWork) -> None:
		"""Initialize the auth-event persistence service.

		Args:
			uow: The request-scoped database unit of work used for auth-event
				persistence.
		"""
		self._uow = uow

	async def persist(self, payload: AuthEventCreateSchema) -> AuthEventSchema:
		"""Persist a canonical auth event.

		Args:
			payload: The canonical auth-event payload to persist.

		Returns:
			The persisted auth-event schema.
		"""
		auth_event_model = await self._uow.auth_events.create_auth_event(payload)
		await self._uow.commit()
		return AuthEventSchema.model_validate(auth_event_model)

	async def persist_batch(
		self,
		payloads: list[AuthEventCreateSchema],
	) -> int:
		"""Persist canonical auth events in a batch.

		Args:
			payloads: The canonical auth-event payloads to persist together.

		Returns:
			The number of created auth events.
		"""
		created_count = await self._uow.auth_events.create_auth_events(payloads)
		await self._uow.commit()
		return created_count
