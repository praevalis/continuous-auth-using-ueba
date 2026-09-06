from dataclasses import dataclass

import numpy as np
import torch

from ml.artifacts import LoadedModelArtifacts
from ml.preparation import PreparedFeatureSet


@dataclass(slots=True)
class ScoringResult:
	"""Component and fused anomaly scores for one auth event."""

	model_version: str
	global_anomaly_score: float
	local_anomaly_score_raw: float
	local_anomaly_score_normalized: float
	fusion_alpha: float
	fused_anomaly_score: float


class HybridScoringService:
	"""Score prepared feature sets with the hybrid anomaly model."""

	def score_event(
		self,
		*,
		prepared_features: PreparedFeatureSet,
		artifacts: LoadedModelArtifacts,
		fusion_alpha: float | None = None,
	) -> ScoringResult:
		"""Score a prepared auth event using the trained hybrid model artifacts.

		Args:
			prepared_features: The prepared feature vectors for the target event.
			artifacts: The loaded trained model artifacts.
			fusion_alpha: The optional fusion alpha override for this score.

		Returns:
			The component and fused anomaly scores for the target event.
		"""
		global_vector = self._select_feature_vector(
			prepared_features,
			artifacts.metadata.autoencoder_features,
		)
		user_vector = self._select_feature_vector(
			prepared_features,
			artifacts.metadata.isolation_forest_features,
		)
		global_input = artifacts.global_scaler.transform(global_vector.reshape(1, -1))
		user_input = artifacts.user_scaler.transform(user_vector.reshape(1, -1))

		global_tensor = torch.tensor(global_input, dtype=torch.float32)
		with torch.no_grad():
			reconstruction = artifacts.autoencoder(global_tensor)

		reconstruction_error = float(
			((reconstruction - global_tensor) ** 2).mean().item()
		)
		local_anomaly_score_raw = float(
			artifacts.isolation_forest.decision_function(user_input)[0]
		)
		normalization = artifacts.metadata.score_normalization or {}
		clip_normalized_scores = bool(normalization.get('clip', False))
		scaled_reconstruction_error = self._safe_minmax_scale(
			reconstruction_error,
			minimum=artifacts.metadata.reconstruction_error_min,
			maximum=artifacts.metadata.reconstruction_error_max,
			clip=clip_normalized_scores,
		)
		scaled_user_score = self._safe_inverse_minmax_scale(
			local_anomaly_score_raw,
			minimum=artifacts.metadata.user_score_min,
			maximum=artifacts.metadata.user_score_max,
			clip=clip_normalized_scores,
		)
		resolved_alpha = (
			fusion_alpha
			if fusion_alpha is not None
			else artifacts.metadata.fusion_alpha
		)
		fused_anomaly_score = (
			resolved_alpha * scaled_user_score
			+ (1 - resolved_alpha) * scaled_reconstruction_error
		)

		return ScoringResult(
			model_version=artifacts.metadata.model_version,
			global_anomaly_score=reconstruction_error,
			local_anomaly_score_raw=local_anomaly_score_raw,
			local_anomaly_score_normalized=scaled_user_score,
			fusion_alpha=resolved_alpha,
			fused_anomaly_score=float(fused_anomaly_score),
		)

	@staticmethod
	def _select_feature_vector(
		prepared_features: PreparedFeatureSet,
		feature_names: list[str],
	) -> np.ndarray:
		try:
			return np.asarray(
				[
					prepared_features.feature_values[feature_name]
					for feature_name in feature_names
				],
				dtype=float,
			)
		except KeyError as error:
			msg = f'Unsupported model feature: {error.args[0]}'
			raise ValueError(msg) from error

	@staticmethod
	def _safe_minmax_scale(
		value: float,
		*,
		minimum: float,
		maximum: float,
		clip: bool = False,
	) -> float:
		"""Scale a value into the ``[0, 1]`` range using min-max scaling.

		Args:
			value: The value to scale.
			minimum: The lower bound observed during training.
			maximum: The upper bound observed during training.
			clip: Whether to constrain the scaled value to ``[0, 1]``.

		Returns:
			The min-max scaled value, or ``0.0`` when the range is degenerate.
		"""
		if np.isclose(maximum, minimum):
			return 0.0
		scaled_value = float((value - minimum) / (maximum - minimum))
		return float(np.clip(scaled_value, 0.0, 1.0)) if clip else scaled_value

	@staticmethod
	def _safe_inverse_minmax_scale(
		value: float,
		*,
		minimum: float,
		maximum: float,
		clip: bool = False,
	) -> float:
		"""Scale a value into the inverted ``[0, 1]`` range using min-max scaling.

		Args:
			value: The value to scale.
			minimum: The lower bound observed during training.
			maximum: The upper bound observed during training.
			clip: Whether to constrain the scaled value to ``[0, 1]``.

		Returns:
			The inverse min-max scaled value, or ``0.0`` when the range is
			degenerate.
		"""
		if np.isclose(maximum, minimum):
			return 0.0
		scaled_value = float((maximum - value) / (maximum - minimum))
		return float(np.clip(scaled_value, 0.0, 1.0)) if clip else scaled_value
