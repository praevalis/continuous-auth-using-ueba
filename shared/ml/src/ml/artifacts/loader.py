import json
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import torch

from ml.models import AutoEncoder


@dataclass(slots=True)
class ModelArtifactMetadata:
	"""Metadata describing one trained model artifact bundle."""

	model_version: str
	training_run_name: str
	created_at: datetime
	autoencoder_features: list[str]
	isolation_forest_features: list[str]
	fusion_alpha: float
	thresholds: dict[str, float]
	feature_engineering_version: int
	reconstruction_error_min: float
	reconstruction_error_max: float
	user_score_min: float
	user_score_max: float
	artifact_files: dict[str, str]
	metadata: dict[str, Any] | None


@dataclass(slots=True)
class LoadedModelArtifacts:
	"""Loaded model artifacts required for online scoring."""

	run_directory: Path
	metadata: ModelArtifactMetadata
	autoencoder: AutoEncoder
	global_scaler: Any
	user_scaler: Any
	isolation_forest: Any


class ModelArtifactLoader:
	def __init__(self, run_directory: Path) -> None:
		"""Initialize the model artifact loader.

		Args:
			run_directory: The training run directory containing model artifacts.
		"""
		self._run_directory = run_directory
		self._loaded_artifacts: LoadedModelArtifacts | None = None

	def load(self) -> LoadedModelArtifacts:
		"""Load and cache model artifacts from the configured run directory.

		Returns:
			The loaded model artifacts required for online scoring.
		"""
		if self._loaded_artifacts is not None:
			return self._loaded_artifacts

		metadata = self._load_metadata(self._run_directory / 'artifact_metadata.json')
		autoencoder = AutoEncoder(input_dim=len(metadata.autoencoder_features))
		state_path = self._run_directory / metadata.artifact_files['autoencoder']
		state_dict = torch.load(state_path, map_location='cpu')
		autoencoder.load_state_dict(state_dict)
		autoencoder.eval()

		global_scaler = self._load_pickle(
			self._run_directory / metadata.artifact_files['global_scaler']
		)
		user_scaler = self._load_pickle(
			self._run_directory / metadata.artifact_files['user_scaler']
		)
		isolation_forest = self._load_pickle(
			self._run_directory / metadata.artifact_files['isolation_forest']
		)

		self._loaded_artifacts = LoadedModelArtifacts(
			run_directory=self._run_directory,
			metadata=metadata,
			autoencoder=autoencoder,
			global_scaler=global_scaler,
			user_scaler=user_scaler,
			isolation_forest=isolation_forest,
		)
		return self._loaded_artifacts

	@staticmethod
	def _load_pickle(path: Path) -> Any:
		"""Load a pickled artifact from disk.

		Args:
			path: The filesystem path to the pickle file.

		Returns:
			The deserialized artifact payload.
		"""
		with path.open('rb') as file_handle:
			return pickle.load(file_handle)

	@staticmethod
	def _load_metadata(path: Path) -> ModelArtifactMetadata:
		"""Load model artifact metadata from disk.

		Args:
			path: The filesystem path to the artifact metadata JSON file.

		Returns:
			The deserialized model artifact metadata.
		"""
		raw_metadata = json.loads(path.read_text(encoding='utf-8'))
		return ModelArtifactMetadata(
			model_version=raw_metadata['model_version'],
			training_run_name=raw_metadata['training_run_name'],
			created_at=datetime.fromisoformat(raw_metadata['created_at']),
			autoencoder_features=list(raw_metadata['autoencoder_features']),
			isolation_forest_features=list(raw_metadata['isolation_forest_features']),
			fusion_alpha=float(raw_metadata['fusion_alpha']),
			thresholds=dict(raw_metadata['thresholds']),
			feature_engineering_version=int(
				raw_metadata['feature_engineering_version']
			),
			reconstruction_error_min=float(raw_metadata['reconstruction_error_min']),
			reconstruction_error_max=float(raw_metadata['reconstruction_error_max']),
			user_score_min=float(raw_metadata['user_score_min']),
			user_score_max=float(raw_metadata['user_score_max']),
			artifact_files=dict(raw_metadata['artifact_files']),
			metadata=raw_metadata.get('metadata'),
		)
