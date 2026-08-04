from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from database import IUnitOfWork
from domain.alert import AlertSeverity, AlertStatus
from domain.enforcement import EnforcementActionStatus, EnforcementActionType
from domain.exceptions import TenantOperatingModeNotFoundError
from domain.policy import DefaultPolicyEvaluator, PolicyAction, ScoreBand
from schemas.alert import AlertCreateSchema
from schemas.enforcement import (
	EnforcementActionCreateSchema,
	EnforcementActionUpdateSchema,
)
from schemas.policy import PolicyDecisionCreateSchema


@dataclass(slots=True)
class PolicyProcessingResult:
	"""Persisted identifiers emitted by one policy evaluation run.

	Attributes:
		policy_decision_id: The persisted policy decision identifier.
		alert_id: The persisted alert identifier when one was created.
		enforcement_action_id: The persisted enforcement action identifier when one
			was created.
	"""

	policy_decision_id: str
	alert_id: str | None
	enforcement_action_id: str | None


class AuthEventPolicyService:
	"""Evaluate policy outcomes for persisted risk scores."""

	def __init__(self, uow: IUnitOfWork) -> None:
		"""Initialize the auth-event policy service.

		Args:
			uow: The unit of work used for policy-side persistence.
		"""
		self._uow = uow
		self._policy_evaluator = DefaultPolicyEvaluator()

	async def process_risk_score(self, risk_score_id: UUID) -> PolicyProcessingResult:
		"""Evaluate policy for a persisted risk score and store its outputs.

		Args:
			risk_score_id: The persisted risk score identifier to evaluate.

		Returns:
			The persisted policy artifact identifiers for the processed score.

		Raises:
			TenantOperatingModeNotFoundError: If no active operating mode exists for
				the tenant at the score timestamp.
		"""
		risk_score = await self._uow.risk_scores.get_risk_score_by_id_or_raise(
			risk_score_id
		)
		auth_event = await self._uow.auth_events.get_auth_event_by_id_or_raise(
			risk_score.auth_event_id
		)

		operating_mode = (
			await self._uow.tenant_operating_modes.get_active_operating_mode_for_tenant(
				risk_score.tenant_id,
				risk_score.scored_at,
			)
		)
		if operating_mode is None:
			raise TenantOperatingModeNotFoundError(
				f'No active operating mode exists for tenant "{risk_score.tenant_id}".'
			)

		recommended_action = self._policy_evaluator.determine_recommended_action(
			risk_score.score_band
		)
		final_action = self._policy_evaluator.determine_final_action(
			recommended_action,
			operating_mode.mode,
		)

		policy_decision = await self._uow.policy_decisions.create_policy_decision(
			PolicyDecisionCreateSchema(
				tenant_id=risk_score.tenant_id,
				auth_event_id=risk_score.auth_event_id,
				risk_score_id=risk_score.id,
				operating_mode_id=operating_mode.id,
				decision_band=risk_score.score_band,
				recommended_action=recommended_action,
				final_action=final_action,
				decision_reason=self._build_decision_reason(
					risk_score.score_band,
					recommended_action,
					final_action,
				),
				decision_metadata={
					'model_version': risk_score.model_version,
					'processing_run_id': str(risk_score.processing_run_id),
					'fused_anomaly_score': risk_score.fused_anomaly_score,
					'caution_threshold_applied': risk_score.caution_threshold_applied,
					'lockout_threshold_applied': risk_score.lockout_threshold_applied,
					'operating_mode': operating_mode.mode.value,
				},
				decided_at=datetime.now(UTC),
			)
		)

		alert_id: str | None = None
		if self._should_create_alert(final_action, risk_score.score_band):
			alert = await self._uow.alerts.create_alert(
				AlertCreateSchema(
					tenant_id=risk_score.tenant_id,
					policy_decision_id=policy_decision.id,
					risk_score_id=risk_score.id,
					severity=self._resolve_alert_severity(risk_score.score_band),
					status=AlertStatus.OPEN,
					title=self._build_alert_title(risk_score.score_band),
					summary=self._build_alert_summary(
						risk_score.score_band,
						final_action,
						risk_score.fused_anomaly_score,
					),
					alert_metadata={
						'auth_event_id': str(risk_score.auth_event_id),
						'operating_mode': operating_mode.mode.value,
						'recommended_action': recommended_action.value,
						'final_action': final_action.value,
					},
				)
			)
			alert_id = str(alert.id)

		enforcement_action_id: str | None = None
		enforcement_action_type = self._resolve_enforcement_action_type(final_action)
		if enforcement_action_type is not None:
			# TODO (Akshat): Replace this temporary mock enforcement path with a real
			# provider adapter from `shared/integrations` once the first end-to-end
			# integration target is selected.
			enforcement_action = (
				await self._uow.enforcement_actions.create_enforcement_action(
					EnforcementActionCreateSchema(
						tenant_id=risk_score.tenant_id,
						policy_decision_id=policy_decision.id,
						event_source_id=auth_event.event_source_id,
						action_type=enforcement_action_type,
						target_user_hash=auth_event.user_hash,
						integration_name='mock_idp',
						request_payload_redacted={
							'action': enforcement_action_type.value,
							'target_user_hash': auth_event.user_hash,
						},
						status=EnforcementActionStatus.PENDING,
						attempt_count=1,
						requested_at=datetime.now(UTC),
					)
				)
			)

			# TODO (Akshat): Replace the synthetic completion result below with the actual
			# provider response payload, external action identifier, and failure
			# handling returned by the outbound enforcement integration.
			enforcement_action = await self._uow.enforcement_actions.update_enforcement_action(
				enforcement_action.id,
				EnforcementActionUpdateSchema(
					status=EnforcementActionStatus.SUCCEEDED,
					external_action_id=(
						f'mock-{enforcement_action_type.value}-{enforcement_action.id}'
					),
					completed_at=datetime.now(UTC),
				),
			)
			enforcement_action_id = str(enforcement_action.id)

		await self._uow.commit()
		return PolicyProcessingResult(
			policy_decision_id=str(policy_decision.id),
			alert_id=alert_id,
			enforcement_action_id=enforcement_action_id,
		)

	@staticmethod
	def _build_decision_reason(
		score_band: ScoreBand,
		recommended_action: PolicyAction,
		final_action: PolicyAction,
	) -> str:
		"""Build a concise reason string for the persisted policy decision.

		Args:
			score_band: The evaluated score band.
			recommended_action: The action implied by the score band.
			final_action: The action after applying operating mode rules.

		Returns:
			A concise decision reason.
		"""
		return (
			f'Score band "{score_band.value}" recommended '
			f'"{recommended_action.value}" and resolved to "{final_action.value}".'
		)

	@staticmethod
	def _should_create_alert(
		final_action: PolicyAction,
		score_band: ScoreBand,
	) -> bool:
		"""Return whether a policy outcome should open an alert.

		Args:
			final_action: The action after applying operating mode rules.
			score_band: The evaluated score band.

		Returns:
			True when an alert should be created for the decision.
		"""
		return (
			score_band is not ScoreBand.SAFE and final_action is not PolicyAction.NONE
		)

	@staticmethod
	def _resolve_alert_severity(score_band: ScoreBand) -> AlertSeverity:
		"""Resolve alert severity from a score band.

		Args:
			score_band: The evaluated score band.

		Returns:
			The alert severity implied by the score band.
		"""
		if score_band is ScoreBand.LOCKOUT:
			return AlertSeverity.HIGH
		return AlertSeverity.MEDIUM

	@staticmethod
	def _build_alert_title(score_band: ScoreBand) -> str:
		"""Build an alert title for a score band.

		Args:
			score_band: The evaluated score band.

		Returns:
			The alert title.
		"""
		if score_band is ScoreBand.LOCKOUT:
			return 'Lockout-risk authentication event detected'
		return 'Caution-risk authentication event detected'

	@staticmethod
	def _build_alert_summary(
		score_band: ScoreBand,
		final_action: PolicyAction,
		fused_anomaly_score: float,
	) -> str:
		"""Build an alert summary for a policy outcome.

		Args:
			score_band: The evaluated score band.
			final_action: The action after applying operating mode rules.
			fused_anomaly_score: The fused anomaly score that triggered the outcome.

		Returns:
			The alert summary.
		"""
		return (
			f'Event classified as "{score_band.value}" with fused score '
			f'{fused_anomaly_score:.4f}; final action is "{final_action.value}".'
		)

	@staticmethod
	def _resolve_enforcement_action_type(
		final_action: PolicyAction,
	) -> EnforcementActionType | None:
		"""Resolve an enforcement action type from a final policy action.

		Args:
			final_action: The action after applying operating mode rules.

		Returns:
			The matching enforcement action type when one should be executed,
			otherwise ``None``.
		"""
		if final_action is PolicyAction.STEP_UP_MFA:
			return EnforcementActionType.STEP_UP_MFA

		if final_action is PolicyAction.TERMINATE_SESSION:
			return EnforcementActionType.TERMINATE_SESSION

		if final_action is PolicyAction.LOCK_ACCOUNT:
			return EnforcementActionType.LOCK_ACCOUNT

		return None
