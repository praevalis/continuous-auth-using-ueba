from uuid import UUID

from domain.exceptions import (
	AlertNotFoundError,
	PolicyDecisionNotFoundError,
	RiskScoreNotFoundError,
	TenantNotFoundError,
)
from schemas.alert import AlertCreateSchema, AlertFilterParams, AlertUpdateSchema
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import AlertModel


class AlertRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the alert repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_alert(self, payload: AlertCreateSchema) -> AlertModel:
		"""Persist an alert.

		Args:
			payload: The alert creation payload.

		Returns:
			The persisted alert model.
		"""
		alert = AlertModel(**payload.model_dump())
		self._session.add(alert)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(error, 'fk_alerts_tenant_id_tenants'):
				raise TenantNotFoundError(
					f'Tenant "{payload.tenant_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_alerts_policy_decision_id_policy_decisions'
			):
				raise PolicyDecisionNotFoundError(
					f'Policy decision "{payload.policy_decision_id}" does not exist.'
				) from error

			if self._matches_constraint(error, 'fk_alerts_risk_score_id_risk_scores'):
				raise RiskScoreNotFoundError(
					f'Risk score "{payload.risk_score_id}" does not exist.'
				) from error

			raise

		await self._session.refresh(alert)
		return alert

	async def update_alert(
		self,
		alert_id: UUID,
		payload: AlertUpdateSchema,
	) -> AlertModel:
		"""Persist updates to an alert.

		Args:
			alert_id: The alert identifier to update.
			payload: The alert update payload.

		Returns:
			The updated alert model.

		Raises:
			AlertNotFoundError: If the alert does not exist.
		"""
		alert = await self.get_alert_by_id_or_raise(alert_id)

		for field_name, field_value in payload.model_dump(exclude_unset=True).items():
			setattr(alert, field_name, field_value)

		await self._session.flush()
		await self._session.refresh(alert)
		return alert

	async def get_alert_by_id(self, alert_id: UUID) -> AlertModel | None:
		"""Return an alert by identifier, if present.

		Args:
			alert_id: The alert identifier to resolve.

		Returns:
			The matching alert model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(AlertModel).where(AlertModel.id == alert_id)
		)
		return result.scalar_one_or_none()

	async def get_alert_by_id_or_raise(self, alert_id: UUID) -> AlertModel:
		"""Return an alert by identifier or raise if it is missing.

		Args:
			alert_id: The alert identifier to resolve.

		Returns:
			The matching alert model.

		Raises:
			AlertNotFoundError: If the alert does not exist.
		"""
		alert = await self.get_alert_by_id(alert_id)
		if alert is None:
			raise AlertNotFoundError(f'Alert "{alert_id}" does not exist.')

		return alert

	async def list_alerts_for_tenant(
		self,
		tenant_id: UUID,
		filters: AlertFilterParams,
	) -> list[AlertModel]:
		"""Return alerts for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Alert filter parameters.

		Returns:
			The alert models associated with the tenant.
		"""
		statement = select(AlertModel).where(AlertModel.tenant_id == tenant_id)

		if filters.policy_decision_id is not None:
			statement = statement.where(
				AlertModel.policy_decision_id == filters.policy_decision_id
			)

		if filters.risk_score_id is not None:
			statement = statement.where(
				AlertModel.risk_score_id == filters.risk_score_id
			)

		if filters.severity is not None:
			statement = statement.where(AlertModel.severity == filters.severity)

		if filters.status is not None:
			statement = statement.where(AlertModel.status == filters.status)

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
