from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from domain.exceptions import (
	AuthEventNotFoundError,
	TenantThresholdProfileNotFoundError,
)
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import AuthEventModel, TenantThresholdProfileModel


@dataclass(slots=True)
class ScoringAuthEventRecord:
	id: UUID
	tenant_id: UUID
	occurred_at: datetime
	user_hash: str
	host_hash: str | None
	occurred_hour: int
	occurred_day_of_week: int


@dataclass(slots=True)
class ScoringThresholdProfileRecord:
	id: UUID
	caution_threshold: float
	lockout_threshold: float
	fusion_alpha: float | None


@dataclass(slots=True)
class ScoringContext:
	window_start: datetime
	auth_event: ScoringAuthEventRecord
	user_history: list[ScoringAuthEventRecord]
	tenant_history: list[ScoringAuthEventRecord]
	threshold_profile: ScoringThresholdProfileRecord


class ScoringQueryService:
	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the scoring query service.

		Args:
			session: The async SQLAlchemy session backing read queries.
		"""
		self._session = session

	async def get_scoring_context(
		self,
		auth_event_id: UUID,
		*,
		history_window_days: int,
	) -> ScoringContext:
		"""Return the read model required to score a single auth event.

		Args:
			auth_event_id: The auth event identifier to score.
			history_window_days: The bounded lookback window size in days.

		Returns:
			The scoring read model composed from the target event, bounded history,
			and active threshold profile.
		"""
		auth_event = await self._get_auth_event_or_raise(auth_event_id)
		window_start = auth_event.occurred_at - timedelta(days=history_window_days)
		threshold_profile = await self._get_active_threshold_profile_or_raise(
			auth_event.tenant_id,
			as_of=auth_event.occurred_at,
		)
		user_history = await self._list_user_history(
			tenant_id=auth_event.tenant_id,
			user_hash=auth_event.user_hash,
			window_start=window_start,
			window_end=auth_event.occurred_at,
		)
		tenant_history = await self._list_tenant_history(
			tenant_id=auth_event.tenant_id,
			window_start=window_start,
			window_end=auth_event.occurred_at,
		)

		return ScoringContext(
			window_start=window_start,
			auth_event=ScoringAuthEventRecord(
				id=auth_event.id,
				tenant_id=auth_event.tenant_id,
				occurred_at=auth_event.occurred_at,
				user_hash=auth_event.user_hash,
				host_hash=auth_event.host_hash,
				occurred_hour=auth_event.occurred_hour,
				occurred_day_of_week=auth_event.occurred_day_of_week,
			),
			user_history=user_history,
			tenant_history=tenant_history,
			threshold_profile=ScoringThresholdProfileRecord(
				id=threshold_profile.id,
				caution_threshold=threshold_profile.caution_threshold,
				lockout_threshold=threshold_profile.lockout_threshold,
				fusion_alpha=threshold_profile.fusion_alpha,
			),
		)

	async def _get_auth_event_or_raise(self, auth_event_id: UUID) -> AuthEventModel:
		"""Return an auth event by identifier or raise if it is missing.

		Args:
			auth_event_id: The auth event identifier to resolve.

		Returns:
			The matching auth event model.

		Raises:
			AuthEventNotFoundError: If the auth event does not exist.
		"""
		result = await self._session.execute(
			select(AuthEventModel).where(AuthEventModel.id == auth_event_id)
		)
		auth_event = result.scalar_one_or_none()
		if auth_event is None:
			raise AuthEventNotFoundError(
				f'Auth event "{auth_event_id}" does not exist.'
			)
		return auth_event

	async def _get_active_threshold_profile_or_raise(
		self,
		tenant_id: UUID,
		*,
		as_of: datetime,
	) -> TenantThresholdProfileModel:
		"""Return the active threshold profile for a tenant or raise if missing.

		Args:
			tenant_id: The owning tenant identifier.
			as_of: The point in time the threshold profile should be active for.

		Returns:
			The matching active threshold profile model.

		Raises:
			TenantThresholdProfileNotFoundError: If no active threshold profile
				exists for the tenant at the provided time.
		"""
		statement = (
			select(TenantThresholdProfileModel)
			.where(
				TenantThresholdProfileModel.tenant_id == tenant_id,
				TenantThresholdProfileModel.is_active.is_(True),
				TenantThresholdProfileModel.effective_from <= as_of,
				or_(
					TenantThresholdProfileModel.effective_to.is_(None),
					TenantThresholdProfileModel.effective_to >= as_of,
				),
			)
			.order_by(TenantThresholdProfileModel.effective_from.desc())
		)
		result = await self._session.execute(statement)
		threshold_profile = result.scalars().first()
		if threshold_profile is None:
			raise TenantThresholdProfileNotFoundError(
				f'No active threshold profile exists for tenant "{tenant_id}".'
			)

		return threshold_profile

	async def _list_user_history(
		self,
		*,
		tenant_id: UUID,
		user_hash: str,
		window_start: datetime,
		window_end: datetime,
	) -> list[ScoringAuthEventRecord]:
		"""Return bounded user history for scoring.

		Args:
			tenant_id: The owning tenant identifier.
			user_hash: The hashed user identifier to resolve history for.
			window_start: The inclusive lower bound of the history window.
			window_end: The exclusive upper bound of the history window.

		Returns:
			The bounded user history records ordered by occurrence time.
		"""
		statement = (
			select(AuthEventModel)
			.where(
				AuthEventModel.tenant_id == tenant_id,
				AuthEventModel.user_hash == user_hash,
				AuthEventModel.occurred_at >= window_start,
				AuthEventModel.occurred_at < window_end,
			)
			.order_by(AuthEventModel.occurred_at.asc(), AuthEventModel.created_at.asc())
		)
		result = await self._session.execute(statement)
		return [
			ScoringAuthEventRecord(
				id=auth_event.id,
				tenant_id=auth_event.tenant_id,
				occurred_at=auth_event.occurred_at,
				user_hash=auth_event.user_hash,
				host_hash=auth_event.host_hash,
				occurred_hour=auth_event.occurred_hour,
				occurred_day_of_week=auth_event.occurred_day_of_week,
			)
			for auth_event in result.scalars().all()
		]

	async def _list_tenant_history(
		self,
		*,
		tenant_id: UUID,
		window_start: datetime,
		window_end: datetime,
	) -> list[ScoringAuthEventRecord]:
		"""Return bounded tenant-wide history for scoring.

		Args:
			tenant_id: The owning tenant identifier.
			window_start: The inclusive lower bound of the history window.
			window_end: The exclusive upper bound of the history window.

		Returns:
			The bounded tenant-wide history records ordered by occurrence time.
		"""
		statement = (
			select(AuthEventModel)
			.where(
				AuthEventModel.tenant_id == tenant_id,
				AuthEventModel.occurred_at >= window_start,
				AuthEventModel.occurred_at < window_end,
			)
			.order_by(AuthEventModel.occurred_at.asc(), AuthEventModel.created_at.asc())
		)
		result = await self._session.execute(statement)
		return [
			ScoringAuthEventRecord(
				id=auth_event.id,
				tenant_id=auth_event.tenant_id,
				occurred_at=auth_event.occurred_at,
				user_hash=auth_event.user_hash,
				host_hash=auth_event.host_hash,
				occurred_hour=auth_event.occurred_hour,
				occurred_day_of_week=auth_event.occurred_day_of_week,
			)
			for auth_event in result.scalars().all()
		]
