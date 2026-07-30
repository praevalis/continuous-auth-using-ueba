from typing import Protocol

from domain.exceptions import InvalidThresholdConfigurationError
from domain.policy.enums import PolicyAction, ScoreBand
from domain.tenant.enums import OperatingMode


class IPolicyEvaluator(Protocol):
	def classify_score_band(
		self,
		fused_anomaly_score: float,
		caution_threshold: float,
		lockout_threshold: float,
	) -> ScoreBand:
		"""Classify a fused anomaly score into a policy band."""
		...

	def determine_recommended_action(self, score_band: ScoreBand) -> PolicyAction:
		"""Determine the recommended action for a score band."""
		...

	def determine_final_action(
		self,
		recommended_action: PolicyAction,
		operating_mode: OperatingMode,
	) -> PolicyAction:
		"""Determine the final action after applying operating mode rules."""
		...


class DefaultPolicyEvaluator:
	def classify_score_band(
		self,
		fused_anomaly_score: float,
		caution_threshold: float,
		lockout_threshold: float,
	) -> ScoreBand:
		"""Classify a fused score into safe, caution, or lockout.

		Args:
			fused_anomaly_score: The computed fused anomaly score.
			caution_threshold: The threshold where caution begins.
			lockout_threshold: The threshold where lockout begins.

		Returns:
			The score band implied by the thresholds.

		Raises:
			InvalidThresholdConfigurationError: If the threshold configuration is
				invalid.
		"""
		if caution_threshold < 0 or lockout_threshold < 0:
			raise InvalidThresholdConfigurationError('Thresholds must be non-negative.')
		if caution_threshold >= lockout_threshold:
			raise InvalidThresholdConfigurationError(
				'Caution threshold must be lower than lockout threshold.'
			)
		if fused_anomaly_score >= lockout_threshold:
			return ScoreBand.LOCKOUT
		if fused_anomaly_score >= caution_threshold:
			return ScoreBand.CAUTION
		return ScoreBand.SAFE

	def determine_recommended_action(self, score_band: ScoreBand) -> PolicyAction:
		"""Determine the recommended policy action for a score band.

		Args:
			score_band: The evaluated score band.

		Returns:
			The recommended policy action before operating mode is applied.
		"""
		if score_band is ScoreBand.SAFE:
			return PolicyAction.ALLOW
		if score_band is ScoreBand.CAUTION:
			return PolicyAction.STEP_UP_MFA
		return PolicyAction.LOCK_ACCOUNT

	def determine_final_action(
		self,
		recommended_action: PolicyAction,
		operating_mode: OperatingMode,
	) -> PolicyAction:
		"""Resolve the final action under the active operating mode.

		Args:
			recommended_action: The recommended action from score evaluation.
			operating_mode: The tenant's active operating mode.

		Returns:
			The action the system should actually take.
		"""
		if operating_mode is OperatingMode.SHADOW:
			return PolicyAction.NONE
		if operating_mode is OperatingMode.ALERT_ONLY:
			if recommended_action is PolicyAction.ALLOW:
				return PolicyAction.ALLOW
			return PolicyAction.ALERT_ONLY
		return recommended_action
