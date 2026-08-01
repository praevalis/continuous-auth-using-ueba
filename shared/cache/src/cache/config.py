from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheSettings(BaseSettings):
	model_config = SettingsConfigDict(
		extra='ignore',
		env_file=('.env', '.env.production', '.env.development'),
	)

	ENVIRONMENT: Literal['development', 'testing', 'production'] = 'development'
	REDIS_HOST: str = 'localhost'
	REDIS_PORT: int = 6380
	REDIS_DB: int = 0
	REDIS_USERNAME: str | None = None
	REDIS_PASSWORD: SecretStr | None = None

	@computed_field(return_type=str)
	@property
	def REDIS_URL(self) -> str:
		"""Build the async Redis URL.

		Returns:
			A Redis URL assembled from the configured components.
		"""
		scheme = 'rediss' if self.ENVIRONMENT == 'production' else 'redis'
		auth_segment = ''
		if self.REDIS_USERNAME is not None or self.REDIS_PASSWORD is not None:
			username = quote_plus(self.REDIS_USERNAME or '')
			password = quote_plus(
				self.REDIS_PASSWORD.get_secret_value() if self.REDIS_PASSWORD else ''
			)
			auth_segment = f'{username}:{password}@'

		return f'{scheme}://{auth_segment}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}'


@lru_cache
def get_cache_settings() -> CacheSettings:
	"""Return the cached cache settings singleton.

	Returns:
		The cached cache settings instance.
	"""
	return CacheSettings()
