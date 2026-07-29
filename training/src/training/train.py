import argparse
import random
from pathlib import Path

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from training.artifacts import prepare_output_directory, save_training_artifacts
from training.config import TrainingConfig, load_config
from training.constants import AUTOENCODER_FEATURES, ISOLATION_FOREST_FEATURES
from training.data import load_dataset
from training.features import engineer_features, select_feature_matrices
from training.fusion import fuse_scores
from training.models import train_autoencoder, train_isolation_forest


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description='Train the UEBA hybrid model pipeline.'
	)
	parser.add_argument(
		'--config',
		type=Path,
		default=Path('training/configs/default.yaml'),
		help='Path to the YAML configuration file.',
	)
	parser.add_argument(
		'--no-gpu',
		action='store_true',
		help='Force CPU training even when CUDA is available.',
	)
	return parser.parse_args()


def set_random_seeds(seed: int) -> None:
	random.seed(seed)
	np.random.seed(seed)
	torch.manual_seed(seed)
	if torch.cuda.is_available():
		torch.cuda.manual_seed_all(seed)


def train_pipeline(config: TrainingConfig, use_gpu: bool = True) -> Path:
	set_random_seeds(config.split.random_state)

	raw_dataframe = load_dataset(config.data)
	feature_dataframe = engineer_features(raw_dataframe, config.data)
	global_features, user_features = select_feature_matrices(feature_dataframe)

	X_global_train, X_global_val = train_test_split(
		global_features,
		test_size=config.split.test_size,
		random_state=config.split.random_state,
	)
	X_user_train, X_user_val = train_test_split(
		user_features,
		test_size=config.split.test_size,
		random_state=config.split.random_state,
	)

	global_scaler = StandardScaler()
	user_scaler = StandardScaler()
	X_global_train_scaled = global_scaler.fit_transform(X_global_train)
	X_global_val_scaled = global_scaler.transform(X_global_val)
	X_user_train_scaled = user_scaler.fit_transform(X_user_train)
	X_user_val_scaled = user_scaler.transform(X_user_val)

	autoencoder_result = train_autoencoder(
		train_values=X_global_train_scaled,
		val_values=X_global_val_scaled,
		config=config.autoencoder,
		use_gpu=use_gpu,
	)
	isolation_forest_result = train_isolation_forest(
		train_values=X_user_train_scaled,
		val_values=X_user_val_scaled,
		config=config.isolation_forest,
	)
	fusion_result = fuse_scores(
		reconstruction_errors=autoencoder_result.val_reconstruction_errors,
		user_scores=isolation_forest_result.validation_scores,
		alpha=config.fusion.alpha,
		threshold_percentiles=config.fusion.threshold_percentiles,
	)

	run_directory = prepare_output_directory(
		output_dir=config.artifacts.output_dir,
		run_name=config.artifacts.run_name,
	)
	metrics = {
		'dataset_rows': len(raw_dataframe),
		'feature_rows': len(feature_dataframe),
		'autoencoder_features': AUTOENCODER_FEATURES,
		'isolation_forest_features': ISOLATION_FOREST_FEATURES,
		'autoencoder': {
			'device': 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu',
			'train_loss_history': autoencoder_result.train_loss_history,
			'val_loss_history': autoencoder_result.val_loss_history,
			'final_train_loss': autoencoder_result.train_loss_history[-1],
			'final_val_loss': autoencoder_result.val_loss_history[-1],
		},
		'isolation_forest': {
			'validation_score_min': float(
				np.min(isolation_forest_result.validation_scores)
			),
			'validation_score_max': float(
				np.max(isolation_forest_result.validation_scores)
			),
		},
		'fusion': {
			'alpha': config.fusion.alpha,
			'thresholds': fusion_result.thresholds,
			'anomaly_score_min': float(np.min(fusion_result.anomaly_scores)),
			'anomaly_score_max': float(np.max(fusion_result.anomaly_scores)),
		},
	}
	save_training_artifacts(
		run_directory=run_directory,
		config=config,
		autoencoder_state=autoencoder_result.model.state_dict(),
		global_scaler=global_scaler,
		user_scaler=user_scaler,
		isolation_forest_model=isolation_forest_result.model,
		metrics=metrics,
	)
	return run_directory


def main() -> None:
	args = parse_args()
	config = load_config(args.config)
	run_directory = train_pipeline(config, use_gpu=not args.no_gpu)
	print(f'Training artifacts written to: {run_directory}')


if __name__ == '__main__':
	main()
