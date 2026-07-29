import pandas as pd

from training.config import DataConfig


def load_dataset(config: DataConfig) -> pd.DataFrame:
	dataset_path = config.dataset_path
	if not dataset_path.exists():
		msg = f'Dataset not found: {dataset_path}'
		raise FileNotFoundError(msg)

	dataframe = pd.read_csv(dataset_path)
	if config.row_limit is not None:
		dataframe = dataframe.iloc[: config.row_limit].copy()

	return dataframe
