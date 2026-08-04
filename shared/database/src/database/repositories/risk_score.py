from uuid import UUID

from domain.exceptions import (
	AuthEventNotFoundError,
	EventProcessingRunNotFoundError,
	FeatureSnapshotNotFoundError,
	RiskScoreNotFoundError,
	TenantNotFoundError,
	TenantThresholdProfileNotFoundError,
)
from schemas.scoring import RiskScoreCreateSchema, RiskScoreFilterParams
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RiskScoreModel


class RiskScoreRepository:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the risk score repository.

		Args:
			session: The async SQLAlchemy session backing repository operations.
		"""
		self._session = session

	async def create_risk_score(
		self,
		payload: RiskScoreCreateSchema,
	) -> RiskScoreModel:
		"""Persist a risk score.

		Args:
			payload: The risk score creation payload.

		Returns:
			The persisted risk score model.
		"""
		risk_score = RiskScoreModel(**payload.model_dump())
		self._session.add(risk_score)

		try:
			await self._session.flush()
		except IntegrityError as error:
			if self._matches_constraint(error, 'fk_risk_scores_tenant_id_tenants'):
				raise TenantNotFoundError(
					f'Tenant "{payload.tenant_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_risk_scores_auth_event_id_auth_events'
			):
				raise AuthEventNotFoundError(
					f'Auth event "{payload.auth_event_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_risk_scores_feature_snapshot_id_feature_snapshots'
			):
				raise FeatureSnapshotNotFoundError(
					f'Feature snapshot "{payload.feature_snapshot_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error, 'fk_risk_scores_processing_run_id_event_processing_runs'
			):
				raise EventProcessingRunNotFoundError(
					f'Event processing run "{payload.processing_run_id}" does not exist.'
				) from error

			if self._matches_constraint(
				error,
				'fk_risk_scores_threshold_profile_id_tenant_threshold_profiles',
			):
				raise TenantThresholdProfileNotFoundError(
					f'Tenant threshold profile "{payload.threshold_profile_id}" does not exist.'
				) from error
			raise

		await self._session.refresh(risk_score)
		return risk_score

	async def get_risk_score_by_id(
		self,
		risk_score_id: UUID,
	) -> RiskScoreModel | None:
		"""Return a risk score by identifier, if present.

		Args:
			risk_score_id: The risk score identifier to resolve.

		Returns:
			The matching risk score model when found, otherwise ``None``.
		"""
		result = await self._session.execute(
			select(RiskScoreModel).where(RiskScoreModel.id == risk_score_id)
		)
		return result.scalar_one_or_none()

	async def get_risk_score_by_id_or_raise(
		self,
		risk_score_id: UUID,
	) -> RiskScoreModel:
		"""Return a risk score by identifier or raise if it is missing.

		Args:
			risk_score_id: The risk score identifier to resolve.

		Returns:
			The matching risk score model.

		Raises:
			RiskScoreNotFoundError: If the risk score does not exist.
		"""
		risk_score = await self.get_risk_score_by_id(risk_score_id)
		if risk_score is None:
			raise RiskScoreNotFoundError(
				f'Risk score "{risk_score_id}" does not exist.'
			)

		return risk_score

	async def list_risk_scores_for_tenant(
		self,
		tenant_id: UUID,
		filters: RiskScoreFilterParams,
	) -> list[RiskScoreModel]:
		"""Return risk scores for a tenant.

		Args:
			tenant_id: The owning tenant identifier.
			filters: Risk score filter parameters.

		Returns:
			The risk score models associated with the tenant.
		"""
		statement = select(RiskScoreModel).where(RiskScoreModel.tenant_id == tenant_id)

		if filters.auth_event_id is not None:
			statement = statement.where(
				RiskScoreModel.auth_event_id == filters.auth_event_id
			)
		if filters.processing_run_id is not None:
			statement = statement.where(
				RiskScoreModel.processing_run_id == filters.processing_run_id
			)
		if filters.threshold_profile_id is not None:
			statement = statement.where(
				RiskScoreModel.threshold_profile_id == filters.threshold_profile_id
			)
		if filters.score_band is not None:
			statement = statement.where(RiskScoreModel.score_band == filters.score_band)

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
