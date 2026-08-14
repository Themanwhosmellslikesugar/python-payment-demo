"""Настройки сервиса."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки из переменных окружения."""

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    database_host: str = 'localhost'
    database_port: int = 5433
    database_user: str = 'postgres'
    database_password: str = 'postgres'  # noqa: S105
    database_db: str = 'payments'
    rabbitmq_url: str = 'amqp://guest:guest@localhost:5673/'
    api_key: str = 'dev-api-key'

    webhook_retry_attempts: int = 3
    consumer_max_attempts: int = 3
    outbox_poll_interval: float = 1.0

    @property
    def database_url(self) -> str:
        """DSN для SQLAlchemy, собранный из частей."""
        return (
            f'postgresql+psycopg://{self.database_user}:{self.database_password}'
            f'@{self.database_host}:{self.database_port}/{self.database_db}'
        )


@lru_cache
def get_settings() -> Settings:
    """Вернуть кешированные настройки."""
    return Settings()
