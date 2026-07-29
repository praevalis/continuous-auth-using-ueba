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
	) -> ScoreBand: ...

	def determine_recommended_action(self, score_band: ScoreBand) -> PolicyAction: ...

	def determine_final_action(
		self,
		recommended_action: PolicyAction,
		operating_mode: OperatingMode,
	) -> PolicyAction: ...


class DefaultPolicyEvaluator:
	def classify_score_band(
		self,
		fused_anomaly_score: float,
		caution_threshold: float,
		lockout_threshold: float,
	) -> ScoreBand:
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
		if operating_mode is OperatingMode.SHADOW:
			return PolicyAction.NONE
		if operating_mode is OperatingMode.ALERT_ONLY:
			if recommended_action is PolicyAction.ALLOW:
				return PolicyAction.ALLOW
			return PolicyAction.ALERT_ONLY
		return recommended_action
