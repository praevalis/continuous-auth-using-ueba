from functools import lru_cache
from typing import Literal

from database import DatabaseSettings
from event_broker import EventBrokerSettings
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
	model_config = SettingsConfigDict(
		extra='ignore',
		env_file=('.env', '.env.production', '.env.development'),
	)

	ENVIRONMENT: Literal['development', 'testing', 'production'] = 'development'
	WORKER_LOG_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = 'INFO'
	AUTH_EVENT_INGESTION_STREAM_NAME: str = 'auth_event_ingestion'
	AUTH_EVENT_NORMALIZATION_CONSUMER_GROUP: str = 'auth_event_normalizers'
	AUTH_EVENT_NORMALIZATION_CONSUMER_NAME: str = 'worker_1'
	AUTH_EVENT_NORMALIZATION_BATCH_SIZE: int = 10
	AUTH_EVENT_NORMALIZATION_BLOCK_MS: int = 5000

	@property
	def database_settings(self) -> DatabaseSettings:
		"""Return the shared database settings for the worker runtime.

		Returns:
			The database settings composed for the current worker environment.
		"""
		return DatabaseSettings(ENVIRONMENT=self.ENVIRONMENT)

	@property
	def event_broker_settings(self) -> EventBrokerSettings:
		"""Return the shared event broker settings for the worker runtime.

		Returns:
			The event broker settings composed for the current worker environment.
		"""
		return EventBrokerSettings(ENVIRONMENT=self.ENVIRONMENT)


@lru_cache
def get_worker_settings() -> WorkerSettings:
	"""Return the cached worker settings singleton.

	Returns:
		The cached worker settings instance.
	"""
	return WorkerSettings()
