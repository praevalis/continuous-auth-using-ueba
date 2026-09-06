from dataclasses import dataclass

import numpy as np


def _safe_minmax_scale(
	values: np.ndarray,
	*,
	minimum: float,
	maximum: float,
) -> np.ndarray:
	if np.isclose(maximum, minimum):
		return np.zeros_like(values, dtype=float)
	return (values - minimum) / (maximum - minimum)


def _safe_inverse_minmax_scale(
	values: np.ndarray,
	*,
	minimum: float,
	maximum: float,
) -> np.ndarray:
	if np.isclose(maximum, minimum):
		return np.zeros_like(values, dtype=float)
	return (maximum - values) / (maximum - minimum)


@dataclass(slots=True)
class FusionResult:
	scaled_reconstruction_errors: np.ndarray
	scaled_user_scores: np.ndarray
	anomaly_scores: np.ndarray
	thresholds: dict[str, float]
	reconstruction_error_min: float
	reconstruction_error_max: float
	user_score_min: float
	user_score_max: float


def fuse_scores(
	reconstruction_errors: np.ndarray,
	user_scores: np.ndarray,
	alpha: float,
	threshold_percentiles: list[int],
	reconstruction_error_range: tuple[float, float] | None = None,
	user_score_range: tuple[float, float] | None = None,
) -> FusionResult:
	reconstruction_error_min, reconstruction_error_max = (
		reconstruction_error_range
		if reconstruction_error_range is not None
		else (
			float(np.min(reconstruction_errors)),
			float(np.max(reconstruction_errors)),
		)
	)
	user_score_min, user_score_max = (
		user_score_range
		if user_score_range is not None
		else (float(np.min(user_scores)), float(np.max(user_scores)))
	)
	scaled_reconstruction_errors = _safe_minmax_scale(
		reconstruction_errors,
		minimum=reconstruction_error_min,
		maximum=reconstruction_error_max,
	)
	scaled_user_scores = _safe_inverse_minmax_scale(
		user_scores,
		minimum=user_score_min,
		maximum=user_score_max,
	)
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
		reconstruction_error_min=reconstruction_error_min,
		reconstruction_error_max=reconstruction_error_max,
		user_score_min=user_score_min,
		user_score_max=user_score_max,
	)
