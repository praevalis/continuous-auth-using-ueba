import networkx as nx
import numpy as np
import pandas as pd

from training.config import DataConfig
from training.constants import AUTOENCODER_FEATURES, ISOLATION_FOREST_FEATURES


def _entropy(series: pd.Series) -> float:
	probabilities = series.value_counts(normalize=True)
	return float(-(probabilities * np.log2(probabilities)).sum())


def _top_ratio(series: pd.Series) -> float:
	counts = series.value_counts(normalize=True)
	return float(counts.iloc[0]) if not counts.empty else 0.0


def engineer_features(dataframe: pd.DataFrame, config: DataConfig) -> pd.DataFrame:
	frame = dataframe.copy()
	timestamp_column = config.timestamp_column
	user_column = config.user_column
	host_column = config.host_column

	timestamp_values = frame[timestamp_column].to_numpy()
	frame['datetime'] = pd.to_datetime(
		timestamp_values,
		unit=config.timestamp_unit,
		origin=config.timestamp_origin,
	)
	frame = frame.sort_values([user_column, 'datetime']).reset_index(drop=True)

	frame['hour_of_day'] = frame['datetime'].dt.hour
	frame['day_of_week'] = frame['datetime'].dt.dayofweek

	frame['login_frequency'] = (
		frame.groupby(user_column)['datetime']
		.transform(
			lambda values: values.diff().dt.total_seconds().rsub(3600).clip(lower=0)
		)
		.fillna(0)
	)
	frame['inter_event_time'] = (
		frame.groupby(user_column)['datetime'].diff().dt.total_seconds().fillna(0)
	)
	frame['avg_inter_event_time'] = (
		frame.groupby(user_column)['inter_event_time'].transform('mean').fillna(0)
	)
	frame['time_since_last_login'] = (
		frame.groupby(user_column)['datetime'].diff().dt.total_seconds().fillna(0)
	)

	user_hosts = frame.groupby(user_column)[host_column].nunique()
	frame = frame.merge(user_hosts.rename('unique_hosts'), on=user_column)

	entropy_map = frame.groupby(user_column)[host_column].apply(_entropy)
	frame = frame.merge(entropy_map.rename('host_entropy'), on=user_column)

	ratio_map = frame.groupby(user_column)[host_column].apply(_top_ratio)
	frame = frame.merge(ratio_map.rename('top_host_ratio'), on=user_column)

	graph = nx.Graph()
	graph.add_edges_from(
		frame[[user_column, host_column]].itertuples(index=False, name=None)
	)
	centrality = nx.degree_centrality(graph)
	user_centrality = {
		user: centrality[user]
		for user in frame[user_column].unique()
		if user in centrality
	}
	frame['degree_centrality'] = frame[user_column].map(user_centrality).fillna(0)

	return frame


def select_feature_matrices(
	dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
	global_features = dataframe[AUTOENCODER_FEATURES].fillna(0)
	user_features = dataframe[ISOLATION_FOREST_FEATURES].fillna(0)
	return global_features, user_features
