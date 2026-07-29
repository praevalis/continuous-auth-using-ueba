from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest

from training.config import IsolationForestConfig


@dataclass(slots=True)
class IsolationForestTrainingResult:
	model: IsolationForest
	validation_scores: np.ndarray
	validation_predictions: np.ndarray


def train_isolation_forest(
	train_values: np.ndarray,
	val_values: np.ndarray,
	config: IsolationForestConfig,
) -> IsolationForestTrainingResult:
	model = IsolationForest(
		n_estimators=config.n_estimators,
		contamination=config.contamination,
		max_samples=float(config.max_samples),
		random_state=config.random_state,
	)
	model.fit(train_values)

	validation_scores = model.decision_function(val_values)
	validation_predictions = model.predict(val_values)

	return IsolationForestTrainingResult(
		model=model,
		validation_scores=validation_scores,
		validation_predictions=validation_predictions,
	)
