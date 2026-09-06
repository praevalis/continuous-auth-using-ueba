import argparse
import random
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler

from training.artifacts import prepare_output_directory, save_training_artifacts
from training.config import TrainingConfig, load_config
from training.constants import (
	AUTOENCODER_FEATURES,
	FEATURE_ENGINEERING_VERSION,
	ISOLATION_FOREST_FEATURES,
)
from training.data import load_dataset, load_test_dataset
from training.features import engineer_features, select_feature_matrices
from training.fusion import fuse_scores
from training.models import (
	compute_reconstruction_errors,
	train_autoencoder,
	train_isolation_forest,
)

_DATASET_SOURCE_COLUMN = '_dataset_source'


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


def _split_chronologically(
	dataframe: pd.DataFrame,
	*,
	timestamp_column: str,
	validation_fraction: float,
	test_fraction: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, float, float | None]:
	if not 0 < validation_fraction < 1:
		raise ValueError('Validation fraction must be between zero and one.')
	if not 0 <= test_fraction < 1:
		raise ValueError('Test fraction must be at least zero and less than one.')
	if validation_fraction + test_fraction >= 1:
		raise ValueError(
			'Validation and test fractions must leave a non-empty training period.'
		)
	minimum_timestamp = float(dataframe[timestamp_column].min())
	maximum_timestamp = float(dataframe[timestamp_column].max())
	timestamp_range = maximum_timestamp - minimum_timestamp
	validation_cutoff = minimum_timestamp + (
		timestamp_range * (1 - validation_fraction - test_fraction)
	)
	test_cutoff = (
		maximum_timestamp - (timestamp_range * test_fraction)
		if test_fraction > 0
		else None
	)
	train_frame = dataframe[dataframe[timestamp_column] < validation_cutoff].copy()
	if test_cutoff is None:
		validation_frame = dataframe[
			dataframe[timestamp_column] >= validation_cutoff
		].copy()
	else:
		validation_frame = dataframe[
			(dataframe[timestamp_column] >= validation_cutoff)
			& (dataframe[timestamp_column] < test_cutoff)
		].copy()
	test_frame = (
		dataframe.iloc[0:0].copy()
		if test_cutoff is None
		else dataframe[dataframe[timestamp_column] >= test_cutoff].copy()
	)
	if train_frame.empty or validation_frame.empty:
		raise ValueError('Chronological split produced an empty partition.')
	if test_fraction > 0 and test_frame.empty:
		raise ValueError('Chronological split produced an empty test partition.')
	return (
		train_frame,
		validation_frame,
		test_frame,
		validation_cutoff,
		test_cutoff,
	)


def _score_summary(values: np.ndarray) -> dict[str, float]:
	return {
		'min': float(np.min(values)),
		'max': float(np.max(values)),
		'mean': float(np.mean(values)),
		'p50': float(np.percentile(values, 50)),
		'p95': float(np.percentile(values, 95)),
		'p99': float(np.percentile(values, 99)),
	}


def train_pipeline(config: TrainingConfig, use_gpu: bool = True) -> Path:
	set_random_seeds(config.split.random_state)

	development_dataframe = load_dataset(config.data)
	development_dataframe[_DATASET_SOURCE_COLUMN] = 'development'
	test_dataframe = load_test_dataset(config.data)
	frames = [development_dataframe]
	if test_dataframe is not None:
		if config.split.test_fraction > 0:
			raise ValueError(
				'Configure either an external test dataset or an internal test fraction, '
				'not both.'
			)
		if float(test_dataframe[config.data.timestamp_column].min()) <= float(
			development_dataframe[config.data.timestamp_column].max()
		):
			raise ValueError(
				'Test dataset must begin after the development dataset ends.'
			)
		test_dataframe[_DATASET_SOURCE_COLUMN] = 'test'
		frames.append(test_dataframe)

	combined_dataframe = pd.concat(frames, ignore_index=True)
	feature_dataframe = engineer_features(combined_dataframe, config.data)
	development_features = feature_dataframe[
		feature_dataframe[_DATASET_SOURCE_COLUMN] == 'development'
	].copy()
	external_test_features = feature_dataframe[
		feature_dataframe[_DATASET_SOURCE_COLUMN] == 'test'
	].copy()
	(
		train_features,
		validation_features,
		internal_test_features,
		validation_cutoff,
		test_cutoff,
	) = _split_chronologically(
		dataframe=development_features,
		timestamp_column=config.data.timestamp_column,
		validation_fraction=config.split.validation_fraction,
		test_fraction=config.split.test_fraction,
	)
	test_features = (
		external_test_features
		if not external_test_features.empty
		else internal_test_features
	)

	X_global_train, X_user_train = select_feature_matrices(train_features)
	X_global_val, X_user_val = select_feature_matrices(validation_features)
	X_global_test, X_user_test = (
		select_feature_matrices(test_features)
		if not test_features.empty
		else (None, None)
	)

	global_scaler = StandardScaler()
	user_scaler = StandardScaler()
	X_global_train_scaled = global_scaler.fit_transform(X_global_train)
	X_global_val_scaled = global_scaler.transform(X_global_val)
	X_user_train_scaled = user_scaler.fit_transform(X_user_train)
	X_user_val_scaled = user_scaler.transform(X_user_val)
	X_global_test_scaled = (
		None if X_global_test is None else global_scaler.transform(X_global_test)
	)
	X_user_test_scaled = (
		None if X_user_test is None else user_scaler.transform(X_user_test)
	)

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
		normalization_strategy=config.fusion.normalization_strategy,
		normalization_lower_percentile=(config.fusion.normalization_lower_percentile),
		normalization_upper_percentile=(config.fusion.normalization_upper_percentile),
	)
	test_metrics: dict[str, object] | None = None
	if X_global_test_scaled is not None and X_user_test_scaled is not None:
		test_reconstruction_errors = compute_reconstruction_errors(
			autoencoder_result.model,
			X_global_test_scaled,
			config.autoencoder.batch_size,
		)
		test_user_scores = isolation_forest_result.model.decision_function(
			X_user_test_scaled
		)
		test_fusion_result = fuse_scores(
			reconstruction_errors=test_reconstruction_errors,
			user_scores=test_user_scores,
			alpha=config.fusion.alpha,
			threshold_percentiles=[],
			normalization_strategy=config.fusion.normalization_strategy,
			normalization_lower_percentile=(
				config.fusion.normalization_lower_percentile
			),
			normalization_upper_percentile=(
				config.fusion.normalization_upper_percentile
			),
			reconstruction_error_range=(
				fusion_result.reconstruction_error_min,
				fusion_result.reconstruction_error_max,
			),
			user_score_range=(
				fusion_result.user_score_min,
				fusion_result.user_score_max,
			),
		)
		test_metrics = {
			'rows': len(test_features),
			'reconstruction_error': _score_summary(test_reconstruction_errors),
			'user_score': _score_summary(test_user_scores),
			'anomaly_score': _score_summary(test_fusion_result.anomaly_scores),
			'threshold_exceedance_rates': {
				threshold_name: float(
					np.mean(test_fusion_result.anomaly_scores >= threshold)
				)
				for threshold_name, threshold in fusion_result.thresholds.items()
			},
		}

	run_directory = prepare_output_directory(
		output_dir=config.artifacts.output_dir,
		run_name=config.artifacts.run_name,
	)
	metrics = {
		'dataset_rows': len(development_dataframe),
		'test_dataset_rows': 0 if test_dataframe is None else len(test_dataframe),
		'feature_rows': len(feature_dataframe),
		'split': {
			'train_rows': len(train_features),
			'validation_rows': len(validation_features),
			'test_rows': len(test_features),
			'validation_cutoff_timestamp': validation_cutoff,
			'test_cutoff_timestamp': test_cutoff,
			'train_timestamp_min': float(
				train_features[config.data.timestamp_column].min()
			),
			'train_timestamp_max': float(
				train_features[config.data.timestamp_column].max()
			),
			'validation_timestamp_min': float(
				validation_features[config.data.timestamp_column].min()
			),
			'validation_timestamp_max': float(
				validation_features[config.data.timestamp_column].max()
			),
			'test_timestamp_min': (
				None
				if test_features.empty
				else float(test_features[config.data.timestamp_column].min())
			),
			'test_timestamp_max': (
				None
				if test_features.empty
				else float(test_features[config.data.timestamp_column].max())
			),
		},
		'autoencoder_features': AUTOENCODER_FEATURES,
		'isolation_forest_features': ISOLATION_FOREST_FEATURES,
		'autoencoder': {
			'device': 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu',
			'architecture': {
				'input_dim': autoencoder_result.model.input_dim,
				'hidden_dim': autoencoder_result.model.hidden_dim,
				'bottleneck_dim': autoencoder_result.model.bottleneck_dim,
			},
			'checkpoint_strategy': config.autoencoder.checkpoint_strategy,
			'selected_epoch': autoencoder_result.selected_epoch,
			'selected_val_loss': autoencoder_result.selected_val_loss,
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
			'normalization': {
				'strategy': config.fusion.normalization_strategy,
				'lower_percentile': (config.fusion.normalization_lower_percentile),
				'upper_percentile': (config.fusion.normalization_upper_percentile),
				'clip': config.fusion.normalization_strategy == 'robust_percentile',
			},
			'thresholds': fusion_result.thresholds,
			'anomaly_score_min': float(np.min(fusion_result.anomaly_scores)),
			'anomaly_score_max': float(np.max(fusion_result.anomaly_scores)),
		},
		'test': test_metrics,
	}
	metadata = {
		'model_version': config.artifacts.run_name,
		'training_run_name': config.artifacts.run_name,
		'created_at': datetime.now(UTC).isoformat(),
		'autoencoder_features': AUTOENCODER_FEATURES,
		'isolation_forest_features': ISOLATION_FOREST_FEATURES,
		'autoencoder_architecture': {
			'input_dim': autoencoder_result.model.input_dim,
			'hidden_dim': autoencoder_result.model.hidden_dim,
			'bottleneck_dim': autoencoder_result.model.bottleneck_dim,
		},
		'fusion_alpha': config.fusion.alpha,
		'score_normalization': {
			'strategy': config.fusion.normalization_strategy,
			'lower_percentile': config.fusion.normalization_lower_percentile,
			'upper_percentile': config.fusion.normalization_upper_percentile,
			'clip': config.fusion.normalization_strategy == 'robust_percentile',
		},
		'thresholds': fusion_result.thresholds,
		'feature_engineering_version': FEATURE_ENGINEERING_VERSION,
		'reconstruction_error_min': fusion_result.reconstruction_error_min,
		'reconstruction_error_max': fusion_result.reconstruction_error_max,
		'user_score_min': fusion_result.user_score_min,
		'user_score_max': fusion_result.user_score_max,
		'artifact_files': {
			'autoencoder': 'autoencoder.pth',
			'global_scaler': 'global_scaler.pkl',
			'user_scaler': 'user_scaler.pkl',
			'isolation_forest': 'isolation_forest.pkl',
			'metrics': 'metrics.json',
			'metadata': 'artifact_metadata.json',
			'config_snapshot': 'config.snapshot.yaml',
		},
		'metadata': {
			'threshold_percentiles': config.fusion.threshold_percentiles,
			'random_state': config.split.random_state,
			'autoencoder_checkpoint_strategy': (config.autoencoder.checkpoint_strategy),
			'autoencoder_selected_epoch': autoencoder_result.selected_epoch,
			'history_window_days': config.data.history_window_days,
			'sampling_strategy': config.data.sampling_strategy,
			'validation_strategy': 'chronological',
			'test_strategy': (
				'out_of_time_external'
				if test_dataframe is not None
				else 'out_of_time_internal'
				if config.split.test_fraction > 0
				else None
			),
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
		metadata=metadata,
	)
	return run_directory


def main() -> None:
	args = parse_args()
	config = load_config(args.config)
	run_directory = train_pipeline(config, use_gpu=not args.no_gpu)
	print(f'Training artifacts written to: {run_directory}')


if __name__ == '__main__':
	main()
