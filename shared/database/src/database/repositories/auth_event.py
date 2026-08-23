from dataclasses import dataclass
from typing import Any
from uuid import UUID

from domain.exceptions import AuthEventNotFoundError
from domain.policy import ScoreBand
from schemas.event import AuthEventCreateSchema, AuthEventListFilterParams
from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import AuthEventModel, RiskScoreModel


@dataclass(slots=True)
class AuthEventListRiskScore:
	"""Compact latest risk-score values returned with an event list item."""

	fused_anomaly_score: float
	caution_threshold_applied: float
	lockout_threshold_applied: float
	score_band: ScoreBand


@dataclass(slots=True)
class AuthEventListItem:
	"""An authentication event and its optional latest risk score."""

	event: AuthEventModel
	risk_score: AuthEventListRiskScore | None


@dataclass(slots=True)
class AuthEventListResult:
	items: list[AuthEventListItem]
	total_count: int


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

	async def get_auth_event_for_tenant_by_id_or_raise(
		self,
		tenant_id: UUID,
		auth_event_id: UUID,
	) -> AuthEventModel:
		"""Return a tenant auth event by identifier or raise if it is missing."""
		result = await self._session.execute(
			select(AuthEventModel).where(
				AuthEventModel.tenant_id == tenant_id,
				AuthEventModel.id == auth_event_id,
			)
		)
		auth_event = result.scalar_one_or_none()
		if auth_event is None:
			raise AuthEventNotFoundError(
				f'Auth event "{auth_event_id}" does not exist.'
			)
		return auth_event

	async def list_auth_events_for_tenant(
		self,
		tenant_id: UUID,
		filters: AuthEventListFilterParams,
	) -> AuthEventListResult:
		"""Return a paginated event list for a tenant."""
		latest_score = (
			select(
				RiskScoreModel.auth_event_id.label('risk_score_event_id'),
				RiskScoreModel.fused_anomaly_score,
				RiskScoreModel.caution_threshold_applied,
				RiskScoreModel.lockout_threshold_applied,
				RiskScoreModel.score_band,
				func.row_number()
				.over(
					partition_by=RiskScoreModel.auth_event_id,
					order_by=(
						RiskScoreModel.scored_at.desc(),
						RiskScoreModel.id.desc(),
					),
				)
				.label('score_rank'),
			)
			.where(RiskScoreModel.tenant_id == tenant_id)
			.subquery()
		)
		statement: Any = (
			select(
				AuthEventModel,
				latest_score.c.fused_anomaly_score,
				latest_score.c.caution_threshold_applied,
				latest_score.c.lockout_threshold_applied,
				latest_score.c.score_band,
			)
			.outerjoin(
				latest_score,
				and_(
					latest_score.c.risk_score_event_id == AuthEventModel.id,
					latest_score.c.score_rank == 1,
				),
			)
			.where(AuthEventModel.tenant_id == tenant_id)
		)
		count_statement: Any = (
			select(func.count())
			.select_from(AuthEventModel)
			.where(AuthEventModel.tenant_id == tenant_id)
		)

		statement = self._apply_event_filters(
			statement,
			filters=filters,
		)
		count_statement = self._apply_event_filters(
			count_statement,
			filters=filters,
		)

		order_by = AuthEventModel.occurred_at.desc()
		if filters.sort == 'occurred_at':
			order_by = AuthEventModel.occurred_at.asc()

		rows = await self._session.execute(
			statement.order_by(order_by, AuthEventModel.created_at.desc())
			.limit(filters.limit)
			.offset(filters.offset)
		)
		total_count = (await self._session.execute(count_statement)).scalar_one()
		items: list[AuthEventListItem] = []
		for row in rows:
			event = row[0]
			risk_score = (
				None
				if row[1] is None
				else AuthEventListRiskScore(
					fused_anomaly_score=row[1],
					caution_threshold_applied=row[2],
					lockout_threshold_applied=row[3],
					score_band=row[4],
				)
			)
			items.append(AuthEventListItem(event=event, risk_score=risk_score))
		return AuthEventListResult(items=items, total_count=total_count)

	@staticmethod
	def _apply_event_filters(
		statement: Any,
		*,
		filters: AuthEventListFilterParams,
	) -> Any:
		if filters.occurred_after is not None:
			statement = statement.where(
				AuthEventModel.occurred_at >= filters.occurred_after
			)
		if filters.occurred_before is not None:
			statement = statement.where(
				AuthEventModel.occurred_at <= filters.occurred_before
			)
		if filters.event_source_id is not None:
			statement = statement.where(
				AuthEventModel.event_source_id == filters.event_source_id
			)
		if filters.event_type is not None:
			statement = statement.where(AuthEventModel.event_type == filters.event_type)
		if filters.outcome is not None:
			statement = statement.where(AuthEventModel.outcome == filters.outcome)
		if filters.location_country is not None:
			statement = statement.where(
				AuthEventModel.location_country == filters.location_country
			)
		return statement
