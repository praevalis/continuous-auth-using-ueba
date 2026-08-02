from datetime import datetime
from uuid import UUID, uuid4

from domain.policy import ScoreBand
from domain.scoring import ProcessingJobType, ProcessingRunStatus
from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.base import Base
from database.utils import enum_type


class EventProcessingRunModel(Base):
	__tablename__ = 'event_processing_runs'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id'), nullable=False, index=True
	)
	auth_event_id: Mapped[UUID] = mapped_column(
		ForeignKey('auth_events.id'), nullable=False, index=True
	)
	job_type: Mapped[ProcessingJobType] = mapped_column(
		enum_type(ProcessingJobType, name='processing_job_type'),
		nullable=False,
	)
	status: Mapped[ProcessingRunStatus] = mapped_column(
		enum_type(ProcessingRunStatus, name='processing_run_status'),
		nullable=False,
		index=True,
	)
	attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	correlation_id: Mapped[str | None] = mapped_column(String(255))
	error_code: Mapped[str | None] = mapped_column(String(100))
	error_message: Mapped[str | None] = mapped_column(String(500))
	queued_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)
	started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
	)


class FeatureSnapshotModel(Base):
	__tablename__ = 'feature_snapshots'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id'), nullable=False, index=True
	)
	auth_event_id: Mapped[UUID] = mapped_column(
		ForeignKey('auth_events.id'), nullable=False, index=True
	)
	processing_run_id: Mapped[UUID] = mapped_column(
		ForeignKey('event_processing_runs.id'), nullable=False
	)
	window_start: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	window_end: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
	login_frequency: Mapped[float | None] = mapped_column(Float)
	avg_inter_event_time: Mapped[float | None] = mapped_column(Float)
	time_since_last_login: Mapped[float | None] = mapped_column(Float)
	unique_hosts: Mapped[float | None] = mapped_column(Float)
	host_entropy: Mapped[float | None] = mapped_column(Float)
	top_host_ratio: Mapped[float | None] = mapped_column(Float)
	degree_centrality: Mapped[float | None] = mapped_column(Float)
	hour_of_day: Mapped[int] = mapped_column(Integer, nullable=False)
	day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
	feature_version: Mapped[int] = mapped_column(Integer, nullable=False)
	computed_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)


class HostInteractionSnapshotModel(Base):
	__tablename__ = 'host_interaction_snapshots'
	__table_args__ = (
		UniqueConstraint(
			'tenant_id',
			'auth_event_id',
			'processing_run_id',
			'user_hash',
			'host_hash',
		),
	)

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id'), nullable=False, index=True
	)
	auth_event_id: Mapped[UUID] = mapped_column(
		ForeignKey('auth_events.id'), nullable=False
	)
	processing_run_id: Mapped[UUID] = mapped_column(
		ForeignKey('event_processing_runs.id'), nullable=False
	)
	window_start: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)
	window_end: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)
	user_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
	host_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
	interaction_count: Mapped[int] = mapped_column(Integer, nullable=False)
	last_interaction_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)
	snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False)
	computed_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)


class RiskScoreModel(Base):
	__tablename__ = 'risk_scores'

	id: Mapped[UUID] = mapped_column(
		PGUUID(as_uuid=True),
		primary_key=True,
		default=uuid4,
	)
	tenant_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenants.id'), nullable=False, index=True
	)
	auth_event_id: Mapped[UUID] = mapped_column(
		ForeignKey('auth_events.id'), nullable=False, index=True
	)
	feature_snapshot_id: Mapped[UUID] = mapped_column(
		ForeignKey('feature_snapshots.id'), nullable=False
	)
	processing_run_id: Mapped[UUID] = mapped_column(
		ForeignKey('event_processing_runs.id'), nullable=False
	)
	model_version: Mapped[str] = mapped_column(String(100), nullable=False)
	threshold_profile_id: Mapped[UUID] = mapped_column(
		ForeignKey('tenant_threshold_profiles.id'), nullable=False
	)
	global_anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
	local_anomaly_score_raw: Mapped[float] = mapped_column(Float, nullable=False)
	local_anomaly_score_normalized: Mapped[float] = mapped_column(Float, nullable=False)
	fusion_alpha: Mapped[float] = mapped_column(Float, nullable=False)
	fused_anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
	caution_threshold_applied: Mapped[float] = mapped_column(Float, nullable=False)
	lockout_threshold_applied: Mapped[float] = mapped_column(Float, nullable=False)
	score_band: Mapped[ScoreBand] = mapped_column(
		enum_type(ScoreBand, name='score_band'),
		nullable=False,
		index=True,
	)
	scored_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False, index=True
	)
