import yaml
from pathlib import Path
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class ServiceSettings(BaseModel):
    """Настройка для http."""

    host: str
    port: int


class LoggerSettings(BaseModel):
    """Найстройка логгера."""

    level: str
    output: str


class TimeoutSettings(BaseModel):
    """Настройка timeout."""

    connect: int
    read: int
    write: int
    pool: int


class Settings(BaseSettings):
    """Базовый класс настроек pydantic."""
    service: ServiceSettings
    logger: LoggerSettings
    timeout: TimeoutSettings

    bot_token: SecretStr

    scrapper_url: Optional[str] = None

    kafka_topic: Optional[str] = None
    kafka_bootstrap_servers: Optional[str] = None
    kafka_consumer_group: Optional[str] = None
    kafka_schema_registry_url: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "secrets" / ".env", env_file_encoding="utf-8"
    )


def load_config() -> Settings:
    """Загрузка конфига."""

    with open(Path(__file__).parent.parent / "config.yml", "r") as f:
        data = yaml.safe_load(f)
    return Settings(**data)


settings = load_config()
