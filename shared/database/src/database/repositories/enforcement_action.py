from uuid import UUID

from domain.exceptions import (
	EnforcementActionNotFoundError,
	EventSourceNotFoundError,
	PolicyDecisionNotFoundError,
	TenantNotFoundError,
)
from schemas.enforcement import (
	EnforcementActionCreateSchema,
	EnforcementActionFilterParams,
	EnforcementActionUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import EnforcementActionModel


class EnforcementActionRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the enforcement action repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_enforcement_action(
		self,
		payload: EnforcementActionCreateSchema,
	) -> EnforcementActionModel:
		"""Persist an enforcement action.

		Args:
			payload: The enforcement action creation payload.

		Returns:
			The persisted enforcement action model.
		"""
		enforcement_action = EnforcementActionModel(**payload.model_dump())
		self._session.add(enforcement_action)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(
				error, 'fk_enforcement_actions_tenant_id_tenants'
			):
				raise TenantNotFoundError(
					f'Tenant "{payload.tenant_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error,
				'fk_enforcement_actions_policy_decision_id_policy_decisions',
			):
				raise PolicyDecisionNotFoundError(
					f'Policy decision "{payload.policy_decision_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_enforcement_actions_event_source_id_event_sources'
			):
				raise EventSourceNotFoundError(
					f'Event source "{payload.event_source_id}" does not exist for the tenant.'
				) from error

			raise

		await self._session.refresh(enforcement_action)
		return enforcement_action

	async def update_enforcement_action(
		self,
		enforcement_action_id: UUID,
		payload: EnforcementActionUpdateSchema,
	) -> EnforcementActionModel:
		"""Persist updates to an enforcement action.

		Args:
			enforcement_action_id: The enforcement action identifier to update.
			payload: The enforcement action update payload.

		Returns:
			The updated enforcement action model.

		Raises:
			EnforcementActionNotFoundError: If the enforcement action does not
				exist.
			EventSourceNotFoundError: If the referenced event source does not exist.
		"""
		enforcement_action = await self.get_enforcement_action_by_id_or_raise(
			enforcement_action_id
		)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(enforcement_action, field_name, field_value)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(
				error, 'fk_enforcement_actions_event_source_id_event_sources'
			):
				raise EventSourceNotFoundError(
					f'Event source "{payload.event_source_id}" does not exist for the tenant.'
				) from error

			raise

		await self._session.refresh(enforcement_action)
		return enforcement_action

	async def get_enforcement_action_by_id(
		self,
		enforcement_action_id: UUID,
	) -> EnforcementActionModel | None:
		"""Return an enforcement action by identifier, if present.

		Args:
			enforcement_action_id: The enforcement action identifier to resolve.

		Returns:
			The matching enforcement action model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(EnforcementActionModel).where(
				EnforcementActionModel.id == enforcement_action_id
			)
		)
		return result.scalar_one_or_none()

	async def get_enforcement_action_by_id_or_raise(
		self,
		enforcement_action_id: UUID,
	) -> EnforcementActionModel:
		"""Return an enforcement action by identifier or raise if it is missing.

		Args:
			enforcement_action_id: The enforcement action identifier to resolve.

		Returns:
			The matching enforcement action model.

		Raises:
			EnforcementActionNotFoundError: If the enforcement action does not
				exist.
		"""
		enforcement_action = await self.get_enforcement_action_by_id(
			enforcement_action_id
		)
		if enforcement_action is None:
			raise EnforcementActionNotFoundError(
				f'Enforcement action "{enforcement_action_id}" does not exist.'
			)

		return enforcement_action

	async def list_enforcement_actions_for_tenant(
		self,
		tenant_id: UUID,
		filters: EnforcementActionFilterParams,
	) -> list[EnforcementActionModel]:
		"""Return enforcement actions for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Enforcement action filter parameters.

		Returns:
			The enforcement action models associated with the tenant.
		"""
		statement = select(EnforcementActionModel).where(
			EnforcementActionModel.tenant_id == tenant_id
		)

		if filters.policy_decision_id is not None:
			statement = statement.where(
				EnforcementActionModel.policy_decision_id == filters.policy_decision_id
			)

		if filters.event_source_id is not None:
			statement = statement.where(
				EnforcementActionModel.event_source_id == filters.event_source_id
			)

		if filters.action_type is not None:
			statement = statement.where(
				EnforcementActionModel.action_type == filters.action_type
			)

		if filters.status is not None:
			statement = statement.where(EnforcementActionModel.status == filters.status)

		result = await self._session.execute(statement)
		return list(result.scalars().all())

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
