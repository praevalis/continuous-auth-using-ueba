import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from database import IUnitOfWork
from database.queries import ScoringQueryService
from domain.policy import DefaultPolicyEvaluator
from domain.scoring import ProcessingJobType, ProcessingRunStatus
from ml import FeaturePreparationService, HybridScoringService, ModelArtifactLoader
from schemas.event import AuthEventScoringJobSchema
from schemas.scoring import (
	EventProcessingRunCreateSchema,
	EventProcessingRunUpdateSchema,
	FeatureSnapshotCreateSchema,
	HostInteractionSnapshotCreateSchema,
	RiskScoreCreateSchema,
)


@dataclass(slots=True)
class ScoringPersistenceResult:
	"""Persisted identifiers emitted by one scoring pipeline run.

	Attributes:
		processing_run_id: The persisted event processing run identifier.
		feature_snapshot_id: The persisted feature snapshot identifier.
		risk_score_id: The persisted risk score identifier.
	"""

	processing_run_id: str
	feature_snapshot_id: str
	risk_score_id: str


class AuthEventScoringService:
	def __init__(
		self,
		uow: IUnitOfWork,
		query_service: ScoringQueryService,
		*,
		model_run_directory: Path,
		history_window_days: int,
	) -> None:
		"""Initialize the auth-event scoring service.

		Args:
			uow: The unit of work used for scoring-side persistence.
			query_service: The scoring query service used to load historical inputs.
			model_run_directory: The model artifact run directory to load from.
			history_window_days: The bounded lookback window size in days.
		"""
		self._uow = uow
		self._query_service = query_service
		self._artifact_loader = ModelArtifactLoader(model_run_directory)
		self._feature_preparation_service = FeaturePreparationService()
		self._hybrid_scoring_service = HybridScoringService()
		self._policy_evaluator = DefaultPolicyEvaluator()
		self._history_window_days = history_window_days

	async def process_message(
		self,
		message: dict[str, str],
	) -> ScoringPersistenceResult:
		"""Score one auth-event job and persist its outputs.

		Args:
			message: The Redis Stream message fields representing one scoring job.

		Returns:
			The persisted scoring artifact identifiers for the processed job.
		"""
		job = self._parse_job(message)
		processing_run = (
			await self._uow.event_processing_runs.create_event_processing_run(
				EventProcessingRunCreateSchema(
					tenant_id=job.tenant_id,
					auth_event_id=job.auth_event_id,
					job_type=ProcessingJobType.SCORE_EVENT,
					status=ProcessingRunStatus.QUEUED,
					attempt_count=0,
					queued_at=datetime.now(UTC),
				)
			)
		)
		await self._uow.event_processing_runs.update_event_processing_run(
			processing_run.id,
			EventProcessingRunUpdateSchema(
				status=ProcessingRunStatus.RUNNING,
				attempt_count=1,
				started_at=datetime.now(UTC),
			),
		)

		try:
			context = await self._query_service.get_scoring_context(
				job.auth_event_id,
				history_window_days=self._history_window_days,
			)
			prepared_features = self._feature_preparation_service.prepare_features(
				context
			)
			artifacts = self._artifact_loader.load()
			fusion_alpha = (
				context.threshold_profile.fusion_alpha
				if context.threshold_profile.fusion_alpha is not None
				else artifacts.metadata.fusion_alpha
			)
			scoring_result = self._hybrid_scoring_service.score_event(
				prepared_features=prepared_features,
				artifacts=artifacts,
				fusion_alpha=fusion_alpha,
			)
			score_band = self._policy_evaluator.classify_score_band(
				scoring_result.fused_anomaly_score,
				context.threshold_profile.caution_threshold,
				context.threshold_profile.lockout_threshold,
			)
			computed_at = datetime.now(UTC)
			feature_snapshot = (
				await self._uow.feature_snapshots.create_feature_snapshot(
					FeatureSnapshotCreateSchema(
						tenant_id=job.tenant_id,
						auth_event_id=job.auth_event_id,
						processing_run_id=processing_run.id,
						window_start=prepared_features.window_start,
						window_end=prepared_features.window_end,
						login_frequency=prepared_features.login_frequency,
						avg_inter_event_time=prepared_features.avg_inter_event_time,
						time_since_last_login=prepared_features.time_since_last_login,
						unique_hosts=prepared_features.unique_hosts,
						host_entropy=prepared_features.host_entropy,
						top_host_ratio=prepared_features.top_host_ratio,
						degree_centrality=prepared_features.degree_centrality,
						hour_of_day=prepared_features.hour_of_day,
						day_of_week=prepared_features.day_of_week,
						feature_version=artifacts.metadata.feature_engineering_version,
						computed_at=computed_at,
					)
				)
			)
			await self._uow.host_interaction_snapshots.create_host_interaction_snapshots(
				[
					HostInteractionSnapshotCreateSchema(
						tenant_id=job.tenant_id,
						auth_event_id=job.auth_event_id,
						processing_run_id=processing_run.id,
						window_start=prepared_features.window_start,
						window_end=prepared_features.window_end,
						user_hash=context.auth_event.user_hash,
						host_hash=host_interaction.host_hash,
						interaction_count=host_interaction.interaction_count,
						last_interaction_at=host_interaction.last_interaction_at,
						snapshot_version=artifacts.metadata.feature_engineering_version,
						computed_at=computed_at,
					)
					for host_interaction in prepared_features.host_interactions
				],
			)
			risk_score = await self._uow.risk_scores.create_risk_score(
				RiskScoreCreateSchema(
					tenant_id=job.tenant_id,
					auth_event_id=job.auth_event_id,
					feature_snapshot_id=feature_snapshot.id,
					processing_run_id=processing_run.id,
					model_version=scoring_result.model_version,
					threshold_profile_id=context.threshold_profile.id,
					global_anomaly_score=scoring_result.global_anomaly_score,
					local_anomaly_score_raw=scoring_result.local_anomaly_score_raw,
					local_anomaly_score_normalized=scoring_result.local_anomaly_score_normalized,
					fusion_alpha=scoring_result.fusion_alpha,
					fused_anomaly_score=scoring_result.fused_anomaly_score,
					caution_threshold_applied=context.threshold_profile.caution_threshold,
					lockout_threshold_applied=context.threshold_profile.lockout_threshold,
					score_band=score_band,
					scored_at=computed_at,
				)
			)
			await self._uow.event_processing_runs.update_event_processing_run(
				processing_run.id,
				EventProcessingRunUpdateSchema(
					status=ProcessingRunStatus.SUCCEEDED,
					finished_at=datetime.now(UTC),
				),
			)
			await self._uow.commit()
		except Exception as error:
			await self._uow.event_processing_runs.update_event_processing_run(
				processing_run.id,
				EventProcessingRunUpdateSchema(
					status=ProcessingRunStatus.FAILED,
					finished_at=datetime.now(UTC),
					error_code=error.__class__.__name__,
					error_message=str(error),
				),
			)
			await self._uow.commit()
			raise

		return ScoringPersistenceResult(
			processing_run_id=str(processing_run.id),
			feature_snapshot_id=str(feature_snapshot.id),
			risk_score_id=str(risk_score.id),
		)

	@staticmethod
	def _parse_job(message: dict[str, str]) -> AuthEventScoringJobSchema:
		"""Parse a scoring job from stream message fields.

		Args:
			message: The Redis Stream message fields for one scoring job.

		Returns:
			The parsed auth-event scoring job payload.
		"""
		payload = message.get('payload')
		if payload is not None:
			return AuthEventScoringJobSchema.model_validate(json.loads(payload))
		return AuthEventScoringJobSchema.model_validate(message)
