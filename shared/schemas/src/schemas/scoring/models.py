from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from schemas.base import SchemaModel
from schemas.policy import ScoreBand


class ProcessingJobType(StrEnum):
	SCORE_EVENT = 'score_event'
	SEND_ALERT = 'send_alert'
	ENFORCE_ACTION = 'enforce_action'


class ProcessingRunStatus(StrEnum):
	QUEUED = 'queued'
	RUNNING = 'running'
	SUCCEEDED = 'succeeded'
	FAILED = 'failed'
	DEAD_LETTERED = 'dead_lettered'


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
