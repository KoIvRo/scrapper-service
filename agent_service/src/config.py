import yaml
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class KafkaSettings(BaseModel):
    """Класс настроек kafka."""

    topic: str


class Settings(BaseSettings):
    """Класс настроек приложения."""

    kafka: KafkaSettings


def load_config() -> Settings:
    """Подгрузить конфиг."""

    with open(Path(__file__).parent.parent / "config.yml", "r") as f:
        data = yaml.safe_load(f)

    return Settings(**data)


settings = load_config()
