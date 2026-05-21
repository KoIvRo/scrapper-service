import yaml
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class FiltersSettings(BaseModel):
    """Класс настройка для фильтров."""

    authors: list


class KafkaConsumerSettings(BaseModel):
    """Класс настроек kafka."""

    topic: str


class LoggerSettings(BaseModel):
    """Класс настроек для логгера."""

    level: str
    output: str


class Settings(BaseSettings):
    """Класс настроек приложения."""

    logger: LoggerSettings
    kafka_consumer: KafkaConsumerSettings
    filters: FiltersSettings


def load_config() -> Settings:
    """Подгрузить конфиг."""

    with open(Path(__file__).parent.parent / "config.yml", "r") as f:
        data = yaml.safe_load(f)

    return Settings(**data)


settings = load_config()
