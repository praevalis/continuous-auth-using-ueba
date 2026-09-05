import pandas as pd

from training.config import DataConfig


def load_dataset(config: DataConfig) -> pd.DataFrame:
	dataset_path = config.dataset_path
	if not dataset_path.exists():
		msg = f'Dataset not found: {dataset_path}'
		raise FileNotFoundError(msg)

	required_columns = [
		config.timestamp_column,
		config.user_column,
		config.host_column,
	]
	dataframe = pd.read_csv(
		dataset_path,
		sep=config.delimiter,
		header=0 if config.has_header else None,
		names=None if config.has_header else required_columns,
		nrows=config.row_limit,
	)

	missing_columns = [
		column for column in required_columns if column not in dataframe.columns
	]
	if missing_columns:
		missing = ', '.join(missing_columns)
		msg = f'Dataset is missing required columns: {missing}'
		raise ValueError(msg)

	return dataframe
