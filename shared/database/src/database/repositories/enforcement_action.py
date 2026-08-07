from dataclasses import dataclass
from typing import Any
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
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import EnforcementActionModel


@dataclass(slots=True)
class EnforcementActionListResult:
	items: list[EnforcementActionModel]
	total_count: int


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
	) -> EnforcementActionListResult:
		"""Return a paginated enforcement-action list for a tenant."""
		statement: Any = select(EnforcementActionModel).where(
			EnforcementActionModel.tenant_id == tenant_id
		)
		count_statement: Any = (
			select(func.count())
			.select_from(EnforcementActionModel)
			.where(EnforcementActionModel.tenant_id == tenant_id)
		)

		statement = self._apply_enforcement_action_filters(
			statement,
			filters=filters,
		)
		count_statement = self._apply_enforcement_action_filters(
			count_statement,
			filters=filters,
		)

		order_by = EnforcementActionModel.requested_at.desc()
		if filters.sort == 'requested_at':
			order_by = EnforcementActionModel.requested_at.asc()

		rows = await self._session.execute(
			statement.order_by(order_by, EnforcementActionModel.created_at.desc())
			.limit(filters.limit)
			.offset(filters.offset)
		)
		total_count = (await self._session.execute(count_statement)).scalar_one()
		return EnforcementActionListResult(
			items=list(rows.scalars().all()),
			total_count=total_count,
		)

	async def get_enforcement_action_for_tenant_by_id_or_raise(
		self,
		tenant_id: UUID,
		enforcement_action_id: UUID,
	) -> EnforcementActionModel:
		"""Return a tenant enforcement action by identifier or raise if missing."""
		result = await self._session.execute(
			select(EnforcementActionModel).where(
				EnforcementActionModel.tenant_id == tenant_id,
				EnforcementActionModel.id == enforcement_action_id,
			)
		)
		enforcement_action = result.scalar_one_or_none()
		if enforcement_action is None:
			raise EnforcementActionNotFoundError(
				f'Enforcement action "{enforcement_action_id}" does not exist.'
			)
		return enforcement_action

	@staticmethod
	def _apply_enforcement_action_filters(
		statement: Any,
		*,
		filters: EnforcementActionFilterParams,
	) -> Any:
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
		if filters.integration_name is not None:
			statement = statement.where(
				EnforcementActionModel.integration_name == filters.integration_name
			)
		if filters.status is not None:
			statement = statement.where(EnforcementActionModel.status == filters.status)
		if filters.requested_after is not None:
			statement = statement.where(
				EnforcementActionModel.requested_at >= filters.requested_after
			)
		if filters.requested_before is not None:
			statement = statement.where(
				EnforcementActionModel.requested_at <= filters.requested_before
			)
		if filters.completed_after is not None:
			statement = statement.where(
				EnforcementActionModel.completed_at >= filters.completed_after
			)
		if filters.completed_before is not None:
			statement = statement.where(
				EnforcementActionModel.completed_at <= filters.completed_before
			)
		return statement

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
