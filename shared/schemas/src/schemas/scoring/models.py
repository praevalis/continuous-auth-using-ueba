from datetime import datetime
from uuid import UUID

from domain.policy import ScoreBand
from domain.scoring import ProcessingJobType, ProcessingRunStatus
from pydantic import Field

from schemas.base import SchemaModel


class EventProcessingRunSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	auth_event_id: UUID
	job_type: ProcessingJobType
	status: ProcessingRunStatus
	attempt_count: int = Field(ge=0)
	correlation_id: str | None = None
	error_code: str | None = None
	error_message: str | None = None
	queued_at: datetime
	started_at: datetime | None = None
	finished_at: datetime | None = None
	created_at: datetime


class EventProcessingRunCreateSchema(SchemaModel):
	tenant_id: UUID
	auth_event_id: UUID
	job_type: ProcessingJobType
	status: ProcessingRunStatus
	attempt_count: int = Field(ge=0)
	correlation_id: str | None = None
	error_code: str | None = None
	error_message: str | None = None
	queued_at: datetime
	started_at: datetime | None = None
	finished_at: datetime | None = None


class EventProcessingRunUpdateSchema(SchemaModel):
	status: ProcessingRunStatus | None = None
	attempt_count: int | None = Field(default=None, ge=0)
	correlation_id: str | None = None
	error_code: str | None = None
	error_message: str | None = None
	started_at: datetime | None = None
	finished_at: datetime | None = None


class EventProcessingRunFilterParams(SchemaModel):
	auth_event_id: UUID | None = None
	job_type: ProcessingJobType | None = None
	status: ProcessingRunStatus | None = None


class FeatureSnapshotSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	auth_event_id: UUID
	processing_run_id: UUID
	window_start: datetime | None = None
	window_end: datetime | None = None
	login_frequency: float | None = None
	avg_inter_event_time: float | None = None
	time_since_last_login: float | None = None
	unique_hosts: float | None = None
	host_entropy: float | None = None
	top_host_ratio: float | None = None
	degree_centrality: float | None = None
	hour_of_day: int = Field(ge=0, le=23)
	day_of_week: int = Field(ge=0, le=6)
	feature_version: int = Field(ge=1)
	computed_at: datetime


class FeatureSnapshotCreateSchema(SchemaModel):
	tenant_id: UUID
	auth_event_id: UUID
	processing_run_id: UUID
	window_start: datetime | None = None
	window_end: datetime | None = None
	login_frequency: float | None = None
	avg_inter_event_time: float | None = None
	time_since_last_login: float | None = None
	unique_hosts: float | None = None
	host_entropy: float | None = None
	top_host_ratio: float | None = None
	degree_centrality: float | None = None
	hour_of_day: int = Field(ge=0, le=23)
	day_of_week: int = Field(ge=0, le=6)
	feature_version: int = Field(ge=1)
	computed_at: datetime


class FeatureSnapshotFilterParams(SchemaModel):
	auth_event_id: UUID | None = None
	processing_run_id: UUID | None = None
	feature_version: int | None = Field(default=None, ge=1)


class HostInteractionSnapshotSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	auth_event_id: UUID
	processing_run_id: UUID
	window_start: datetime
	window_end: datetime
	user_hash: str = Field(min_length=1)
	host_hash: str = Field(min_length=1)
	interaction_count: int = Field(ge=0)
	last_interaction_at: datetime
	snapshot_version: int = Field(ge=1)
	computed_at: datetime


class HostInteractionSnapshotCreateSchema(SchemaModel):
	tenant_id: UUID
	auth_event_id: UUID
	processing_run_id: UUID
	window_start: datetime
	window_end: datetime
	user_hash: str = Field(min_length=1)
	host_hash: str = Field(min_length=1)
	interaction_count: int = Field(ge=0)
	last_interaction_at: datetime
	snapshot_version: int = Field(ge=1)
	computed_at: datetime


class HostInteractionSnapshotFilterParams(SchemaModel):
	auth_event_id: UUID | None = None
	processing_run_id: UUID | None = None
	user_hash: str | None = Field(default=None, min_length=1)
	host_hash: str | None = Field(default=None, min_length=1)
	snapshot_version: int | None = Field(default=None, ge=1)


class RiskScoreSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	auth_event_id: UUID
	feature_snapshot_id: UUID
	processing_run_id: UUID
	model_version: str = Field(min_length=1)
	threshold_profile_id: UUID
	global_anomaly_score: float
	local_anomaly_score_raw: float
	local_anomaly_score_normalized: float
	fusion_alpha: float
	fused_anomaly_score: float
	caution_threshold_applied: float
	lockout_threshold_applied: float
	score_band: ScoreBand
	scored_at: datetime


class RiskScoreCreateSchema(SchemaModel):
	tenant_id: UUID
	auth_event_id: UUID
	feature_snapshot_id: UUID
	processing_run_id: UUID
	model_version: str = Field(min_length=1)
	threshold_profile_id: UUID
	global_anomaly_score: float
	local_anomaly_score_raw: float
	local_anomaly_score_normalized: float
	fusion_alpha: float
	fused_anomaly_score: float
	caution_threshold_applied: float
	lockout_threshold_applied: float
	score_band: ScoreBand
	scored_at: datetime


class RiskScoreFilterParams(SchemaModel):
	auth_event_id: UUID | None = None
	processing_run_id: UUID | None = None
	threshold_profile_id: UUID | None = None
	score_band: ScoreBand | None = None


class RiskSummaryFilterParams(SchemaModel):
	"""Optional occurrence-time bounds for a tenant risk summary."""

	occurred_after: datetime | None = None
	occurred_before: datetime | None = None


class RiskSummarySchema(SchemaModel):
	"""Tenant event and scored-risk counts for risk summary consumers."""

	tenant_id: UUID
	occurred_after: datetime | None = None
	occurred_before: datetime | None = None
	event_count: int = Field(ge=0)
	safe_count: int = Field(ge=0)
	caution_count: int = Field(ge=0)
	lockout_count: int = Field(ge=0)
	unscored_count: int = Field(ge=0)
	latest_event_at: datetime | None = None
	latest_scored_at: datetime | None = None
	generated_at: datetime
