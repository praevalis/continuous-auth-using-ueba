AUTOENCODER_FEATURES = [
	'unique_hosts',
	'host_entropy',
	'top_host_ratio',
	'degree_centrality',
	'hour_sin',
	'hour_cos',
	'day_of_week_sin',
	'day_of_week_cos',
]

ISOLATION_FOREST_FEATURES = [
	'login_frequency',
	'avg_inter_event_time',
	'time_since_last_login',
]

FEATURE_ENGINEERING_VERSION = 2
