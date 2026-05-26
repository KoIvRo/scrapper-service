import yaml
from pathlib import Path
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class FiltersSettings(BaseModel):
    """Класс настройка для фильтров."""

    authors: list[str]
    min_length: int
    stop_words: list[str]
    threshold: int
    window_ms: int
    high_words: list[str]
    low_words: list[str]


class LoggerSettings(BaseModel):
    """Класс настроек для логгера."""

    level: str
    output: str


class TimeoutSettings(BaseModel):
    """Класс настроек для timeout."""

    connect: int
    read: int
    write: int
    pool: int


class AISettings(BaseModel):
    """Класс настроек AI API."""

    use_ai: bool
    url: str
    model: str


class CircuitBreakerSettings(BaseModel):
    """Класс настройки CircuitBreker."""

    failure_threshold: int
    recovery_timeout: int


class RetrySettings(BaseModel):
    """Настройка retry."""

    max_attempts: int
    exponential_multiplier: int
    exponential_min_seconds: int
    exponential_max_seconds: int
    status_codes: list[int]


class Settings(BaseSettings):
    """Класс настроек приложения."""

    logger: LoggerSettings
    filters: FiltersSettings
    timeout: TimeoutSettings
    ai: AISettings
    circuit_breaker: CircuitBreakerSettings
    retry: RetrySettings

    kafka_consumer_topic: str = "link.raw-updates"
    kafka_consumer_group: str = "agent-consumer-group"

    kafka_schema_registry_url: str = "http://localhost:8081"
    kafka_bootstrap_servers: str = "localhost:9092,localhost:9093,localhost:9094"

    ai_token: SecretStr

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "secrets" / ".env",
        env_file_encoding="utf-8",
    )


def load_config() -> Settings:
    """Подгрузить конфиг."""

    with open(Path(__file__).parent.parent / "config.yml", "r") as f:
        data = yaml.safe_load(f)

    return Settings(**data)


settings = load_config()
