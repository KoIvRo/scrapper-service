import yaml
from pathlib import Path
from typing import Optional, Literal
from pydantic import SecretStr, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseModel):
    """Настройки scrapper."""

    host: str
    port: int
    access_type: Literal["orm", "raw"]


class RateLimitSettings(BaseModel):
    """Настройка RateLimit."""

    links_get: str
    links_post: str
    links_delete: str
    chats_post: str
    chats_delete: str


class LoggerSettings(BaseModel):
    """Настройка логгера."""

    level: str
    output: str


class ConcurrencySettings(BaseModel):
    """Настройки асинхронности."""

    batch_size: int
    update_time: int
    concurrency_links: int


class TimeoutSettings(BaseModel):
    """Настрйока Timeout."""

    connect: int
    read: int
    write: int
    pool: int


class RetrySettings(BaseModel):
    """Настройка retry."""

    max_attempts: int
    exponential_multiplier: int
    exponential_min_seconds: int
    exponential_max_seconds: int
    status_codes: list[int]


class CircuitBreakerSettings(BaseModel):
    """Настройка CircuitBreaker."""

    failure_threshold: int
    recovery_timeout: int


class OutboxSettings(BaseModel):
    """Настройка Outbox."""

    cleanup_interval: int
    days_to_truncate: int
    update_time: int


class ValkeySettings(BaseModel):
    """Настройка Valkey."""

    ttl: int


class Settings(BaseSettings):
    """Базовый класс настроек pydantic."""

    service: ServiceSettings
    rate_limit: RateLimitSettings
    retry: RetrySettings
    circuit_breaker: CircuitBreakerSettings
    timeout: TimeoutSettings
    concurrency: ConcurrencySettings
    logger: LoggerSettings
    outbox: OutboxSettings
    valkey: ValkeySettings

    github_token: Optional[SecretStr] = None

    bot_url: Optional[str] = None

    kafka_topic: Optional[str] = None
    kafka_bootstrap_servers: Optional[str] = None
    kafka_schema_registry_url: Optional[str] = None

    valkey_host: str = "localhost"
    valkey_port: int = 6379

    postgres_host: Optional[str]
    postgres_port: Optional[int]
    postgres_db: Optional[str]
    postgres_user: Optional[str]
    postgres_password: SecretStr

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "secrets" / ".env", env_file_encoding="utf-8"
    )


def load_config() -> Settings:
    """Загрузка конфига."""

    with open(Path(__file__).parent.parent / "config.yml", "r") as f:
        data = yaml.safe_load(f)

    return Settings(**data)


settings = load_config()
