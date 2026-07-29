from dataclasses import dataclass

import numpy as np


def _safe_minmax_scale(values: np.ndarray) -> np.ndarray:
	minimum = float(np.min(values))
	maximum = float(np.max(values))
	if np.isclose(maximum, minimum):
		return np.zeros_like(values, dtype=float)
	return (values - minimum) / (maximum - minimum)


def _safe_inverse_minmax_scale(values: np.ndarray) -> np.ndarray:
	minimum = float(np.min(values))
	maximum = float(np.max(values))
	if np.isclose(maximum, minimum):
		return np.zeros_like(values, dtype=float)
	return (maximum - values) / (maximum - minimum)


@dataclass(slots=True)
class FusionResult:
	scaled_reconstruction_errors: np.ndarray
	scaled_user_scores: np.ndarray
	anomaly_scores: np.ndarray
	thresholds: dict[str, float]


def fuse_scores(
	reconstruction_errors: np.ndarray,
	user_scores: np.ndarray,
	alpha: float,
	threshold_percentiles: list[int],
) -> FusionResult:
	scaled_reconstruction_errors = _safe_minmax_scale(reconstruction_errors)
	scaled_user_scores = _safe_inverse_minmax_scale(user_scores)
	anomaly_scores = (
		alpha * scaled_user_scores + (1 - alpha) * scaled_reconstruction_errors
	)
	thresholds = {
		f'p{percentile}': float(np.percentile(anomaly_scores, percentile))
		for percentile in threshold_percentiles
	}

	return FusionResult(
		scaled_reconstruction_errors=scaled_reconstruction_errors,
		scaled_user_scores=scaled_user_scores,
		anomaly_scores=anomaly_scores,
		thresholds=thresholds,
	)
