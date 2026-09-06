from dataclasses import dataclass

import numpy as np


def _safe_minmax_scale(
	values: np.ndarray,
	*,
	minimum: float,
	maximum: float,
	clip: bool = False,
) -> np.ndarray:
	if np.isclose(maximum, minimum):
		return np.zeros_like(values, dtype=float)
	scaled_values = (values - minimum) / (maximum - minimum)
	return np.clip(scaled_values, 0.0, 1.0) if clip else scaled_values


def _safe_inverse_minmax_scale(
	values: np.ndarray,
	*,
	minimum: float,
	maximum: float,
	clip: bool = False,
) -> np.ndarray:
	if np.isclose(maximum, minimum):
		return np.zeros_like(values, dtype=float)
	scaled_values = (maximum - values) / (maximum - minimum)
	return np.clip(scaled_values, 0.0, 1.0) if clip else scaled_values


def _normalization_range(
	values: np.ndarray,
	*,
	strategy: str,
	lower_percentile: float,
	upper_percentile: float,
) -> tuple[float, float]:
	if strategy == 'minmax':
		return float(np.min(values)), float(np.max(values))
	if strategy == 'robust_percentile':
		if not 0 <= lower_percentile < upper_percentile <= 100:
			raise ValueError(
				'Normalization percentiles must satisfy 0 <= lower < upper <= 100.'
			)
		return (
			float(np.percentile(values, lower_percentile)),
			float(np.percentile(values, upper_percentile)),
		)
	raise ValueError(f'Unsupported normalization strategy: {strategy}')


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
	normalization_strategy: str = 'minmax',
	normalization_lower_percentile: float = 0,
	normalization_upper_percentile: float = 100,
	reconstruction_error_range: tuple[float, float] | None = None,
	user_score_range: tuple[float, float] | None = None,
) -> FusionResult:
	reconstruction_error_min, reconstruction_error_max = (
		reconstruction_error_range
		if reconstruction_error_range is not None
		else _normalization_range(
			reconstruction_errors,
			strategy=normalization_strategy,
			lower_percentile=normalization_lower_percentile,
			upper_percentile=normalization_upper_percentile,
		)
	)
	user_score_min, user_score_max = (
		user_score_range
		if user_score_range is not None
		else _normalization_range(
			user_scores,
			strategy=normalization_strategy,
			lower_percentile=normalization_lower_percentile,
			upper_percentile=normalization_upper_percentile,
		)
	)
	clip = normalization_strategy == 'robust_percentile'
	scaled_reconstruction_errors = _safe_minmax_scale(
		reconstruction_errors,
		minimum=reconstruction_error_min,
		maximum=reconstruction_error_max,
		clip=clip,
	)
	scaled_user_scores = _safe_inverse_minmax_scale(
		user_scores,
		minimum=user_score_min,
		maximum=user_score_max,
		clip=clip,
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
