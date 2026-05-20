import yaml
from pathlib import Path
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseModel):
    """Настройки для kafka."""

    topic: str
    bootstrap_servers: str
    consumer_group: str
    schema_registry_url: str


class HTTPSettings(BaseModel):
    """Настройка для http."""

    host: str
    port: int
    scrapper_url: str


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

    kafka: KafkaSettings
    http: HTTPSettings
    logger: LoggerSettings
    timeout: TimeoutSettings

    bot_token: SecretStr

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "secrets" / ".env", env_file_encoding="utf-8"
    )


def load_config() -> Settings:
    """Загрузка конфига."""

    with open(Path(__file__).parent.parent / "config.yml", "r") as f:
        data = yaml.safe_load(f)
    return Settings(**data)


settings = load_config()
