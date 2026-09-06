import heapq
from collections import Counter, deque
from dataclasses import dataclass, field
from math import log2, pi

import numpy as np
import pandas as pd

from training.config import DataConfig
from training.constants import AUTOENCODER_FEATURES, ISOLATION_FOREST_FEATURES


def _count_log_count(count: int) -> float:
	return count * log2(count) if count > 0 else 0.0


@dataclass(slots=True)
class _UserWindow:
	events: deque[tuple[float, str]] = field(default_factory=deque)
	host_counts: Counter[str] = field(default_factory=Counter)
	count_log_count_sum: float = 0.0
	max_host_heap: list[tuple[int, str]] = field(default_factory=list)

	def evict_before(self, cutoff: float) -> None:
		while self.events and self.events[0][0] < cutoff:
			_, host = self.events.popleft()
			old_count = self.host_counts[host]
			new_count = old_count - 1
			self.count_log_count_sum += _count_log_count(new_count) - _count_log_count(
				old_count
			)
			if new_count == 0:
				del self.host_counts[host]
			else:
				self.host_counts[host] = new_count
				heapq.heappush(self.max_host_heap, (-new_count, host))

	def preview(self, timestamp: float, host: str) -> tuple[float, ...]:
		if self.events:
			time_since_last_login = timestamp - self.events[-1][0]
			avg_inter_event_time = (timestamp - self.events[0][0]) / (
				len(self.events) + 1
			)
			login_frequency = max(3600.0 - time_since_last_login, 0.0)
		else:
			time_since_last_login = 0.0
			avg_inter_event_time = 0.0
			login_frequency = 0.0

		existing_host_count = self.host_counts.get(host, 0)
		next_host_count = existing_host_count + 1
		event_count = len(self.events) + 1
		unique_hosts = len(self.host_counts) + int(existing_host_count == 0)
		count_log_count_sum = self.count_log_count_sum + (
			_count_log_count(next_host_count) - _count_log_count(existing_host_count)
		)
		host_entropy = log2(event_count) - (count_log_count_sum / event_count)
		top_host_count = max(self._current_max_host_count(), next_host_count)
		top_host_ratio = top_host_count / event_count

		return (
			login_frequency,
			avg_inter_event_time,
			time_since_last_login,
			float(unique_hosts),
			float(host_entropy),
			float(top_host_ratio),
		)

	def append(self, timestamp: float, host: str) -> None:
		old_count = self.host_counts.get(host, 0)
		new_count = old_count + 1
		self.host_counts[host] = new_count
		self.count_log_count_sum += _count_log_count(new_count) - _count_log_count(
			old_count
		)
		heapq.heappush(self.max_host_heap, (-new_count, host))
		self.events.append((timestamp, host))

	def _current_max_host_count(self) -> int:
		while self.max_host_heap:
			negative_count, host = self.max_host_heap[0]
			if self.host_counts.get(host, 0) == -negative_count:
				return -negative_count
			heapq.heappop(self.max_host_heap)
		return 0


@dataclass(slots=True)
class _TenantGraphWindow:
	events: deque[tuple[float, str, str]] = field(default_factory=deque)
	edge_counts: Counter[tuple[str, str]] = field(default_factory=Counter)
	user_degrees: Counter[str] = field(default_factory=Counter)
	host_degrees: Counter[str] = field(default_factory=Counter)

	def evict_before(self, cutoff: float) -> None:
		while self.events and self.events[0][0] < cutoff:
			_, user, host = self.events.popleft()
			edge = (user, host)
			self.edge_counts[edge] -= 1
			if self.edge_counts[edge] > 0:
				continue

			del self.edge_counts[edge]
			self.user_degrees[user] -= 1
			self.host_degrees[host] -= 1
			if self.user_degrees[user] == 0:
				del self.user_degrees[user]
			if self.host_degrees[host] == 0:
				del self.host_degrees[host]

	def preview_degree_centrality(self, user: str, host: str) -> float:
		is_new_edge = (user, host) not in self.edge_counts
		user_degree = self.user_degrees.get(user, 0) + int(is_new_edge)
		node_count = (
			len(self.user_degrees)
			+ len(self.host_degrees)
			+ int(user not in self.user_degrees)
			+ int(host not in self.host_degrees)
		)
		return float(user_degree / (node_count - 1)) if node_count > 1 else 0.0

	def append(self, timestamp: float, user: str, host: str) -> None:
		edge = (user, host)
		if self.edge_counts[edge] == 0:
			self.user_degrees[user] += 1
			self.host_degrees[host] += 1
		self.edge_counts[edge] += 1
		self.events.append((timestamp, user, host))


def engineer_features(dataframe: pd.DataFrame, config: DataConfig) -> pd.DataFrame:
	if config.history_window_days <= 0:
		raise ValueError('Feature history window must be greater than zero days.')
	frame = dataframe.sort_values(
		config.timestamp_column,
		kind='mergesort',
	).reset_index(drop=True)
	timestamps = frame[config.timestamp_column].to_numpy(dtype=float)
	users = frame[config.user_column].astype(str).to_numpy()
	hosts = frame[config.host_column].astype(str).to_numpy()
	datetimes = pd.to_datetime(
		timestamps,
		unit=config.timestamp_unit,
		origin=config.timestamp_origin,
	)
	hours = datetimes.hour.to_numpy()
	days_of_week = datetimes.dayofweek.to_numpy()
	hour_angles = 2 * pi * hours / 24
	day_angles = 2 * pi * days_of_week / 7

	feature_values = np.empty((len(frame), 11), dtype=float)
	user_windows: dict[str, _UserWindow] = {}
	tenant_window = _TenantGraphWindow()
	history_window_seconds = float(config.history_window_days * 24 * 60 * 60)

	group_start = 0
	while group_start < len(frame):
		timestamp = timestamps[group_start]
		group_end = int(np.searchsorted(timestamps, timestamp, side='right'))
		cutoff = timestamp - history_window_seconds
		tenant_window.evict_before(cutoff)

		for index in range(group_start, group_end):
			user = users[index]
			host = hosts[index]
			user_window = user_windows.setdefault(user, _UserWindow())
			user_window.evict_before(cutoff)
			(
				login_frequency,
				avg_inter_event_time,
				time_since_last_login,
				unique_hosts,
				host_entropy,
				top_host_ratio,
			) = user_window.preview(timestamp, host)
			degree_centrality = tenant_window.preview_degree_centrality(user, host)

			feature_values[index] = (
				login_frequency,
				avg_inter_event_time,
				time_since_last_login,
				unique_hosts,
				host_entropy,
				top_host_ratio,
				degree_centrality,
				np.sin(hour_angles[index]),
				np.cos(hour_angles[index]),
				np.sin(day_angles[index]),
				np.cos(day_angles[index]),
			)

		for index in range(group_start, group_end):
			user = users[index]
			host = hosts[index]
			user_windows[user].append(timestamp, host)
			tenant_window.append(timestamp, user, host)

		group_start = group_end

	feature_names = [
		*ISOLATION_FOREST_FEATURES,
		'unique_hosts',
		'host_entropy',
		'top_host_ratio',
		'degree_centrality',
		'hour_sin',
		'hour_cos',
		'day_of_week_sin',
		'day_of_week_cos',
	]
	frame[feature_names] = feature_values
	frame['datetime'] = datetimes
	frame['hour_of_day'] = hours
	frame['day_of_week'] = days_of_week
	return frame


def select_feature_matrices(
	dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
	global_features = dataframe[AUTOENCODER_FEATURES].fillna(0)
	user_features = dataframe[ISOLATION_FOREST_FEATURES].fillna(0)
	return global_features, user_features
