from functools import lru_cache
from typing import Literal

from cache import CacheSettings
from database import DatabaseSettings
from event_broker import EventBrokerSettings
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
	model_config = SettingsConfigDict(
		extra='ignore',
		env_file=('.env', '.env.production', '.env.development'),
	)

	ENVIRONMENT: Literal['development', 'testing', 'production'] = 'development'
	API_HOST: str = '127.0.0.1'
	API_PORT: int = 8000
	API_LOG_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = 'INFO'
	API_CORS_ALLOW_ORIGINS: list[str] = ['http://localhost:5173']
	API_CORS_ALLOW_CREDENTIALS: bool = True
	API_CORS_ALLOW_METHODS: list[str] = ['*']
	API_CORS_ALLOW_HEADERS: list[str] = ['*']
	AUTH_EVENT_INGESTION_STREAM_NAME: str = 'auth_event_ingestion'
	PIPELINE_HEALTH_STALE_AFTER_MINUTES: int = 15
	PIPELINE_HEALTH_FAILURE_LOOKBACK_HOURS: int = 24

	@field_validator(
		'API_CORS_ALLOW_ORIGINS',
		'API_CORS_ALLOW_METHODS',
		'API_CORS_ALLOW_HEADERS',
		mode='before',
	)
	@classmethod
	def parse_csv_list(cls, value: object) -> object:
		"""Normalize comma-separated environment values into lists.

		Args:
			value: The raw environment value provided to the settings field.

		Returns:
			A normalized list when the value is comma-separated text, otherwise the
			original value.
		"""
		if not isinstance(value, str):
			return value

		return [item.strip() for item in value.split(',') if item.strip()]

	@property
	def database_settings(self) -> DatabaseSettings:
		"""Return the shared database settings for the API runtime.

		Returns:
			The database settings composed for the current API environment.
		"""
		return DatabaseSettings(ENVIRONMENT=self.ENVIRONMENT)

	@property
	def cache_settings(self) -> CacheSettings:
		"""Return the shared cache settings for the API runtime.

		Returns:
			The cache settings composed for the current API environment.
		"""
		return CacheSettings(ENVIRONMENT=self.ENVIRONMENT)

	@property
	def event_broker_settings(self) -> EventBrokerSettings:
		"""Return the shared event broker settings for the API runtime.

		Returns:
			The event broker settings composed for the current API environment.
		"""
		return EventBrokerSettings(ENVIRONMENT=self.ENVIRONMENT)


@lru_cache
def get_api_settings() -> ApiSettings:
	"""Return the cached API settings singleton.

	Returns:
		The cached API settings instance.
	"""
	return ApiSettings()
