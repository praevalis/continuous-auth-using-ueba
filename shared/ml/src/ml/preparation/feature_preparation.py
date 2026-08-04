from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from math import log2

import networkx as nx
import numpy as np
from database.queries import ScoringAuthEventRecord, ScoringContext


@dataclass(slots=True)
class PreparedHostInteraction:
	"""Prepared host interaction details for snapshot persistence."""

	host_hash: str
	interaction_count: int
	last_interaction_at: datetime


@dataclass(slots=True)
class PreparedFeatureSet:
	"""Prepared online scoring features for one auth event."""

	window_start: datetime
	window_end: datetime
	login_frequency: float
	avg_inter_event_time: float
	time_since_last_login: float
	unique_hosts: float
	host_entropy: float
	top_host_ratio: float
	degree_centrality: float
	hour_of_day: int
	day_of_week: int
	global_feature_vector: np.ndarray
	user_feature_vector: np.ndarray
	host_interactions: list[PreparedHostInteraction]


class FeaturePreparationService:
	"""Prepare online scoring features from scoring context."""

	def prepare_features(self, context: ScoringContext) -> PreparedFeatureSet:
		"""Prepare training-aligned feature vectors for one auth event.

		Args:
			context: The scoring context composed from persisted historical data.

		Returns:
			The prepared feature set used for scoring and snapshot persistence.
		"""
		target_event = context.auth_event
		user_events = sorted(
			[*context.user_history, target_event],
			key=lambda event: (event.occurred_at, event.id),
		)
		tenant_events = sorted(
			[*context.tenant_history, target_event],
			key=lambda event: (event.occurred_at, event.id),
		)

		time_deltas = self._compute_time_deltas(user_events)
		time_since_last_login = time_deltas[-1] if time_deltas else 0.0
		login_frequency = (
			max(3600.0 - time_since_last_login, 0.0) if time_deltas else 0.0
		)
		avg_inter_event_time = (
			float(sum(time_deltas) / len(time_deltas)) if time_deltas else 0.0
		)

		host_hashes = [
			event.host_hash for event in user_events if event.host_hash is not None
		]
		unique_hosts = float(len(set(host_hashes))) if host_hashes else 0.0
		host_entropy = self._compute_entropy(host_hashes)
		top_host_ratio = self._compute_top_host_ratio(host_hashes)

		degree_centrality, host_interactions = self._compute_graph_features(
			tenant_events=tenant_events,
			target_event=target_event,
		)

		global_feature_vector = np.asarray(
			[
				unique_hosts,
				host_entropy,
				top_host_ratio,
				degree_centrality,
				float(target_event.occurred_hour),
				float(target_event.occurred_day_of_week),
			],
			dtype=float,
		)
		user_feature_vector = np.asarray(
			[
				login_frequency,
				avg_inter_event_time,
				time_since_last_login,
			],
			dtype=float,
		)

		return PreparedFeatureSet(
			window_start=context.window_start,
			window_end=target_event.occurred_at,
			login_frequency=login_frequency,
			avg_inter_event_time=avg_inter_event_time,
			time_since_last_login=time_since_last_login,
			unique_hosts=unique_hosts,
			host_entropy=host_entropy,
			top_host_ratio=top_host_ratio,
			degree_centrality=degree_centrality,
			hour_of_day=target_event.occurred_hour,
			day_of_week=target_event.occurred_day_of_week,
			global_feature_vector=global_feature_vector,
			user_feature_vector=user_feature_vector,
			host_interactions=host_interactions,
		)

	@staticmethod
	def _compute_time_deltas(user_events: list[ScoringAuthEventRecord]) -> list[float]:
		"""Compute inter-event time deltas for ordered user events.

		Args:
			user_events: Ordered user history including the target event.

		Returns:
			The per-event time deltas in seconds, using ``0.0`` for the first event.
		"""
		time_deltas: list[float] = []
		previous_occurred_at: datetime | None = None

		for event in user_events:
			if previous_occurred_at is None:
				time_deltas.append(0.0)
			else:
				time_deltas.append(
					(event.occurred_at - previous_occurred_at).total_seconds()
				)
			previous_occurred_at = event.occurred_at

		return time_deltas

	@staticmethod
	def _compute_entropy(host_hashes: list[str]) -> float:
		"""Compute host entropy for a sequence of host hashes.

		Args:
			host_hashes: The host hashes observed for the scored user.

		Returns:
			The Shannon entropy of the observed host distribution.
		"""
		if not host_hashes:
			return 0.0

		counts = Counter(host_hashes)
		total = sum(counts.values())
		return float(
			-sum(
				(probability := count / total) * log2(probability)
				for count in counts.values()
				if count > 0
			)
		)

	@staticmethod
	def _compute_top_host_ratio(host_hashes: list[str]) -> float:
		"""Compute the most-common-host ratio for a sequence of host hashes.

		Args:
			host_hashes: The host hashes observed for the scored user.

		Returns:
			The normalized ratio of the most frequent host.
		"""
		if not host_hashes:
			return 0.0

		counts = Counter(host_hashes)
		total = sum(counts.values())
		return float(max(counts.values()) / total) if total else 0.0

	@staticmethod
	def _compute_graph_features(
		*,
		tenant_events: list[ScoringAuthEventRecord],
		target_event: ScoringAuthEventRecord,
	) -> tuple[float, list[PreparedHostInteraction]]:
		"""Compute bounded-window graph features for one auth event.

		Args:
			tenant_events: Ordered tenant-wide history including the target event.
			target_event: The target auth event being scored.

		Returns:
			The bounded-window degree centrality and prepared host interactions.
		"""
		graph = nx.Graph()
		host_occurrences: dict[str, int] = defaultdict(int)
		host_last_seen: dict[str, datetime] = {}

		for event in tenant_events:
			if event.host_hash is None:
				continue

			graph.add_edge(event.user_hash, event.host_hash)

			if event.user_hash == target_event.user_hash:
				host_occurrences[event.host_hash] += 1
				host_last_seen[event.host_hash] = event.occurred_at

		centrality = nx.degree_centrality(graph) if graph.number_of_nodes() > 0 else {}
		degree_centrality = float(centrality.get(target_event.user_hash, 0.0))
		host_interactions = [
			PreparedHostInteraction(
				host_hash=host_hash,
				interaction_count=interaction_count,
				last_interaction_at=host_last_seen[host_hash],
			)
			for host_hash, interaction_count in sorted(host_occurrences.items())
		]
		return degree_centrality, host_interactions
