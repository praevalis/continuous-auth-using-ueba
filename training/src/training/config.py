from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

TimestampUnit = Literal['D', 's', 'ms', 'us', 'ns']
TimestampOrigin = Literal['unix'] | str


@dataclass(slots=True)
class DataConfig:
	dataset_path: Path
	row_limit: int | None
	timestamp_column: str
	timestamp_unit: TimestampUnit
	timestamp_origin: TimestampOrigin
	user_column: str
	host_column: str


@dataclass(slots=True)
class SplitConfig:
	test_size: float
	random_state: int


@dataclass(slots=True)
class AutoencoderConfig:
	epochs: int
	learning_rate: float
	batch_size: int


@dataclass(slots=True)
class IsolationForestConfig:
	n_estimators: int
	contamination: float
	max_samples: str | int | float
	random_state: int


@dataclass(slots=True)
class FusionConfig:
	alpha: float
	threshold_percentiles: list[int]


@dataclass(slots=True)
class ArtifactConfig:
	output_dir: Path
	run_name: str


@dataclass(slots=True)
class TrainingConfig:
	data: DataConfig
	split: SplitConfig
	autoencoder: AutoencoderConfig
	isolation_forest: IsolationForestConfig
	fusion: FusionConfig
	artifacts: ArtifactConfig


def load_config(config_path: Path) -> TrainingConfig:
	raw_config = yaml.safe_load(config_path.read_text(encoding='utf-8'))

	return TrainingConfig(
		data=DataConfig(
			dataset_path=Path(raw_config['data']['dataset_path']),
			row_limit=raw_config['data'].get('row_limit'),
			timestamp_column=raw_config['data']['timestamp_column'],
			timestamp_unit=raw_config['data']['timestamp_unit'],
			timestamp_origin=raw_config['data']['timestamp_origin'],
			user_column=raw_config['data']['user_column'],
			host_column=raw_config['data']['host_column'],
		),
		split=SplitConfig(
			test_size=raw_config['split']['test_size'],
			random_state=raw_config['split']['random_state'],
		),
		autoencoder=AutoencoderConfig(
			epochs=raw_config['autoencoder']['epochs'],
			learning_rate=raw_config['autoencoder']['learning_rate'],
			batch_size=raw_config['autoencoder']['batch_size'],
		),
		isolation_forest=IsolationForestConfig(
			n_estimators=raw_config['isolation_forest']['n_estimators'],
			contamination=raw_config['isolation_forest']['contamination'],
			max_samples=raw_config['isolation_forest']['max_samples'],
			random_state=raw_config['isolation_forest']['random_state'],
		),
		fusion=FusionConfig(
			alpha=raw_config['fusion']['alpha'],
			threshold_percentiles=list(raw_config['fusion']['threshold_percentiles']),
		),
		artifacts=ArtifactConfig(
			output_dir=Path(raw_config['artifacts']['output_dir']),
			run_name=raw_config['artifacts']['run_name'],
		),
	)


def config_to_dict(config: TrainingConfig) -> dict[str, Any]:
	return {
		'data': {
			'dataset_path': str(config.data.dataset_path),
			'row_limit': config.data.row_limit,
			'timestamp_column': config.data.timestamp_column,
			'timestamp_unit': config.data.timestamp_unit,
			'timestamp_origin': config.data.timestamp_origin,
			'user_column': config.data.user_column,
			'host_column': config.data.host_column,
		},
		'split': {
			'test_size': config.split.test_size,
			'random_state': config.split.random_state,
		},
		'autoencoder': {
			'epochs': config.autoencoder.epochs,
			'learning_rate': config.autoencoder.learning_rate,
			'batch_size': config.autoencoder.batch_size,
		},
		'isolation_forest': {
			'n_estimators': config.isolation_forest.n_estimators,
			'contamination': config.isolation_forest.contamination,
			'max_samples': config.isolation_forest.max_samples,
			'random_state': config.isolation_forest.random_state,
		},
		'fusion': {
			'alpha': config.fusion.alpha,
			'threshold_percentiles': config.fusion.threshold_percentiles,
		},
		'artifacts': {
			'output_dir': str(config.artifacts.output_dir),
			'run_name': config.artifacts.run_name,
		},
	}
