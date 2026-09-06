import bz2
import gzip
from collections.abc import Iterator
from pathlib import Path
from typing import IO, cast

import numpy as np
import pandas as pd

from training.config import DataConfig


def _open_binary_dataset(dataset_path: Path) -> IO[bytes]:
	if dataset_path.suffix == '.bz2':
		return bz2.open(dataset_path, 'rb')
	if dataset_path.suffix == '.gz':
		return cast(IO[bytes], gzip.open(dataset_path, 'rb'))
	return dataset_path.open('rb')


def _count_dataset_rows(dataset_path: Path, *, has_header: bool) -> int:
	with _open_binary_dataset(dataset_path) as file_handle:
		line_count = 0
		last_byte = b''
		for block in iter(lambda: file_handle.read(8 * 1024 * 1024), b''):
			line_count += block.count(b'\n')
			last_byte = block[-1:]

	if last_byte and last_byte != b'\n':
		line_count += 1
	return max(line_count - int(has_header), 0)


def _read_chunks(
	dataset_path: Path,
	*,
	config: DataConfig,
) -> Iterator[pd.DataFrame]:
	required_columns = _required_columns(config)
	return pd.read_csv(
		dataset_path,
		sep=config.delimiter,
		header=0 if config.has_header else None,
		names=None if config.has_header else required_columns,
		chunksize=config.read_chunk_size,
	)


def _required_columns(config: DataConfig) -> list[str]:
	return [
		config.timestamp_column,
		config.user_column,
		config.host_column,
	]


def _validate_columns(dataframe: pd.DataFrame, config: DataConfig) -> None:
	missing_columns = [
		column
		for column in _required_columns(config)
		if column not in dataframe.columns
	]
	if missing_columns:
		missing = ', '.join(missing_columns)
		msg = f'Dataset is missing required columns: {missing}'
		raise ValueError(msg)


def _load_uniform_sample(
	dataset_path: Path,
	*,
	config: DataConfig,
	row_limit: int,
) -> pd.DataFrame:
	total_rows = _count_dataset_rows(dataset_path, has_header=config.has_header)
	if total_rows == 0:
		raise ValueError(f'Dataset is empty: {dataset_path}')
	if row_limit >= total_rows:
		dataframe = pd.read_csv(
			dataset_path,
			sep=config.delimiter,
			header=0 if config.has_header else None,
			names=None if config.has_header else _required_columns(config),
		)
		_validate_columns(dataframe, config)
		return dataframe

	selected_indices = np.linspace(
		0,
		total_rows - 1,
		num=row_limit,
		dtype=np.int64,
	)
	sampled_chunks: list[pd.DataFrame] = []
	row_offset = 0

	for chunk in _read_chunks(dataset_path, config=config):
		chunk_end = row_offset + len(chunk)
		left = int(np.searchsorted(selected_indices, row_offset, side='left'))
		right = int(np.searchsorted(selected_indices, chunk_end, side='left'))
		if right > left:
			local_indices = selected_indices[left:right] - row_offset
			sampled_chunks.append(chunk.iloc[local_indices])
		row_offset = chunk_end

	dataframe = pd.concat(sampled_chunks, ignore_index=True)
	_validate_columns(dataframe, config)
	return dataframe


def _load_dataset_path(
	dataset_path: Path,
	*,
	config: DataConfig,
	row_limit: int | None,
) -> pd.DataFrame:
	if not dataset_path.exists():
		msg = f'Dataset not found: {dataset_path}'
		raise FileNotFoundError(msg)

	if row_limit is not None and row_limit <= 0:
		raise ValueError('Dataset row limit must be greater than zero.')
	if config.read_chunk_size <= 0:
		raise ValueError('Dataset read chunk size must be greater than zero.')
	if config.sampling_strategy not in {'head', 'uniform'}:
		raise ValueError(
			f'Unsupported dataset sampling strategy: {config.sampling_strategy}'
		)
	if config.sampling_strategy == 'uniform' and row_limit is not None:
		return _load_uniform_sample(
			dataset_path,
			config=config,
			row_limit=row_limit,
		)

	dataframe = pd.read_csv(
		dataset_path,
		sep=config.delimiter,
		header=0 if config.has_header else None,
		names=None if config.has_header else _required_columns(config),
		nrows=row_limit,
	)
	_validate_columns(dataframe, config)
	return dataframe


def load_dataset(config: DataConfig) -> pd.DataFrame:
	return _load_dataset_path(
		config.dataset_path,
		config=config,
		row_limit=config.row_limit,
	)


def load_test_dataset(config: DataConfig) -> pd.DataFrame | None:
	if config.test_dataset_path is None:
		return None
	return _load_dataset_path(
		config.test_dataset_path,
		config=config,
		row_limit=config.test_row_limit,
	)
