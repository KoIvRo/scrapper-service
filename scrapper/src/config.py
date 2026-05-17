from pathlib import Path
from typing import Optional, Literal
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Базовый класс настроек pydantic."""

    host: Optional[str] = None
    port: Optional[int] = None
    access_type: Optional[Literal["mem", "raw", "orm"]] = None
    bot_url: Optional[str] = None

    postgres_db: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: Optional[int] = None
    postgres_password: Optional[SecretStr] = None

    kafka_bootstrap_servers: Optional[str] = None
    kafka_topic: str = "link-updates"
    notification_type: Literal["http", "kafka"] = "kafka"

    github_token: Optional[SecretStr] = None

    logger_level: str = "INFO"
    logger_output: str = "stdout"

    batch_size: int = 100
    update_time: int = 10
    concurrency_links: int = 20

    schema_registry_url: Optional[str] = None

    valkey_host: Optional[str] = None
    valkey_port: Optional[int] = None
    valkey_ttl: Optional[int] = None

    timeout: Optional[int] = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "secrets" / ".env", env_file_encoding="utf-8"
    )


settings = Settings()
