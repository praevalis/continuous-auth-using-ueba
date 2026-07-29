from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.policy.enums import ScoreBand


@dataclass(slots=True)
class RiskScore:
	id: UUID
	tenant_id: UUID
	auth_event_id: UUID
	feature_snapshot_id: UUID
	processing_run_id: UUID
	model_version: str
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
