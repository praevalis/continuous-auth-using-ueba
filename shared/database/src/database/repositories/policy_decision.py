from dataclasses import dataclass
from typing import Any
from uuid import UUID

from domain.exceptions import (
	AuthEventNotFoundError,
	PolicyDecisionNotFoundError,
	RiskScoreNotFoundError,
	TenantNotFoundError,
	TenantOperatingModeNotFoundError,
)
from schemas.policy import PolicyDecisionCreateSchema, PolicyDecisionFilterParams
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import PolicyDecisionModel


@dataclass(slots=True)
class PolicyDecisionListResult:
	items: list[PolicyDecisionModel]
	total_count: int


class PolicyDecisionRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the policy decision repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_policy_decision(
		self,
		payload: PolicyDecisionCreateSchema,
	) -> PolicyDecisionModel:
		"""Persist a policy decision.

		Args:
			payload: The policy decision creation payload.

		Returns:
			The persisted policy decision model.
		"""
		policy_decision = PolicyDecisionModel(**payload.model_dump())
		self._session.add(policy_decision)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(error, 'fk_policy_decisions_tenant_id_tenants'):
				raise TenantNotFoundError(
					f'Tenant "{payload.tenant_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_policy_decisions_auth_event_id_auth_events'
			):
				raise AuthEventNotFoundError(
					f'Auth event "{payload.auth_event_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_policy_decisions_risk_score_id_risk_scores'
			):
				raise RiskScoreNotFoundError(
					f'Risk score "{payload.risk_score_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error,
				'fk_policy_decisions_operating_mode_id_tenant_operating_modes',
			):
				raise TenantOperatingModeNotFoundError(
					f'Tenant operating mode "{payload.operating_mode_id}" does not exist.'
				) from error

			raise

		await self._session.refresh(policy_decision)
		return policy_decision

	async def get_policy_decision_by_id(
		self,
		policy_decision_id: UUID,
	) -> PolicyDecisionModel | None:
		"""Return a policy decision by identifier, if present.

		Args:
			policy_decision_id: The policy decision identifier to resolve.

		Returns:
			The matching policy decision model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(PolicyDecisionModel).where(
				PolicyDecisionModel.id == policy_decision_id
			)
		)
		return result.scalar_one_or_none()

	async def get_policy_decision_by_id_or_raise(
		self,
		policy_decision_id: UUID,
	) -> PolicyDecisionModel:
		"""Return a policy decision by identifier or raise if it is missing.

		Args:
			policy_decision_id: The policy decision identifier to resolve.

		Returns:
			The matching policy decision model.

		Raises:
			PolicyDecisionNotFoundError: If the policy decision does not exist.
		"""
		policy_decision = await self.get_policy_decision_by_id(policy_decision_id)
		if policy_decision is None:
			raise PolicyDecisionNotFoundError(
				f'Policy decision "{policy_decision_id}" does not exist.'
			)

		return policy_decision

	async def list_policy_decisions_for_tenant(
		self,
		tenant_id: UUID,
		filters: PolicyDecisionFilterParams,
	) -> PolicyDecisionListResult:
		"""Return a paginated policy-decision list for a tenant."""
		statement: Any = select(PolicyDecisionModel).where(
			PolicyDecisionModel.tenant_id == tenant_id
		)
		count_statement: Any = (
			select(func.count())
			.select_from(PolicyDecisionModel)
			.where(PolicyDecisionModel.tenant_id == tenant_id)
		)

		statement = self._apply_policy_decision_filters(
			statement,
			filters=filters,
		)
		count_statement = self._apply_policy_decision_filters(
			count_statement,
			filters=filters,
		)

		order_by = PolicyDecisionModel.decided_at.desc()
		if filters.sort == 'decided_at':
			order_by = PolicyDecisionModel.decided_at.asc()

		rows = await self._session.execute(
			statement.order_by(order_by, PolicyDecisionModel.id.desc())
			.limit(filters.limit)
			.offset(filters.offset)
		)
		total_count = (await self._session.execute(count_statement)).scalar_one()
		return PolicyDecisionListResult(
			items=list(rows.scalars().all()),
			total_count=total_count,
		)

	async def get_policy_decision_for_tenant_by_id_or_raise(
		self,
		tenant_id: UUID,
		policy_decision_id: UUID,
	) -> PolicyDecisionModel:
		"""Return a tenant policy decision by identifier or raise if missing."""
		result = await self._session.execute(
			select(PolicyDecisionModel).where(
				PolicyDecisionModel.tenant_id == tenant_id,
				PolicyDecisionModel.id == policy_decision_id,
			)
		)
		policy_decision = result.scalar_one_or_none()
		if policy_decision is None:
			raise PolicyDecisionNotFoundError(
				f'Policy decision "{policy_decision_id}" does not exist.'
			)
		return policy_decision

	@staticmethod
	def _apply_policy_decision_filters(
		statement: Any,
		*,
		filters: PolicyDecisionFilterParams,
	) -> Any:
		if filters.auth_event_id is not None:
			statement = statement.where(
				PolicyDecisionModel.auth_event_id == filters.auth_event_id
			)
		if filters.decision_band is not None:
			statement = statement.where(
				PolicyDecisionModel.decision_band == filters.decision_band
			)
		if filters.final_action is not None:
			statement = statement.where(
				PolicyDecisionModel.final_action == filters.final_action
			)
		if filters.decided_after is not None:
			statement = statement.where(
				PolicyDecisionModel.decided_at >= filters.decided_after
			)
		if filters.decided_before is not None:
			statement = statement.where(
				PolicyDecisionModel.decided_at <= filters.decided_before
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
