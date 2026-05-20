from pathlib import Path
from typing import Optional
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Базовый класс настроек pydantic."""

    host: Optional[str] = None
    port: Optional[int] = None

    scrapper_url: Optional[str] = None

    bot_token: SecretStr

    logger_level: str = "INFO"
    logger_output: str = "stdout"

    kafka_bootstrap_servers: Optional[str] = None
    kafka_topic: str = "link_updates"
    kafka_consumer_group: str = "bot-consumer-group"

    schema_registry_url: Optional[str] = None

    timeout_connect: Optional[int] = None
    timeout_read: Optional[int] = None
    timeout_write: Optional[int] = None
    timeout_pool: Optional[int] = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "secrets" / ".env", env_file_encoding="utf-8"
    )


# Инициализируем общие настройки
settings = Settings()
