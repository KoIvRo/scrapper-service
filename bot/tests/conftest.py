import sys
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent / "src"))
os.environ["BOT_TOKEN"] = "test_token"

from config import settings  # noqa
from updates.api import update
from updates.kafka_consumer import KafkaConsumer


@pytest.fixture
def mock_avro():
    """Мок для Avro десериализатора."""
    with patch.object(KafkaConsumer, "_create_schema_registry"):
        with patch("updates.kafka_consumer.AvroDeserializer") as mock:
            yield mock


@pytest.fixture
def mock_consumer():
    """Мок для confluent-kafka Consumer."""
    with patch("updates.kafka_consumer.Consumer") as mock:
        yield mock


@pytest.fixture
def mock_handle_update():
    """Мок для handle_update."""
    with patch("updates.kafka_consumer.handle_update", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def kafka_consumer(mock_avro, mock_consumer):
    """Экземпляр KafkaConsumer с замоканным consumer."""
    consumer = KafkaConsumer(
        bootstrap_servers="localhost:9092",
        topic="test-topic",
        group_id="test-group",
        schema_registry_url="http://localhost:8081",
    )
    return consumer


@pytest.fixture
def message_factory():
    """Фабрика для создания тестовых сообщений."""

    def create_message(text: str):
        message = AsyncMock()
        message.text = text
        message.from_user.id = 12345
        message.from_user.username = "test_user"
        message.answer = AsyncMock()
        return message

    return create_message


@pytest.fixture
def app_with_mock_bot():
    """Создаёт приложение FastAPI с замоканным ботом."""
    with patch("updates.update_handler.get_bot") as mock_get_bot:
        bot = AsyncMock()
        bot.send_message = AsyncMock()
        mock_get_bot.return_value = bot
        app = FastAPI()
        app.include_router(update)
        yield app, mock_get_bot


@pytest.fixture
def client(app_with_mock_bot):
    """Тестовый клиент FastAPI."""
    app, _ = app_with_mock_bot
    return TestClient(app)


@pytest.fixture
def mock_bot(app_with_mock_bot):
    """Мок для бота."""
    _, mock_get_bot = app_with_mock_bot
    return mock_get_bot


@pytest.fixture
def valid_update_data():
    """Корректные данные для обновления."""
    return {
        "id": 1,
        "url": "https://github.com/user/repo",
        "description": "Test update",
        "tgChatIds": [123, 456],
    }
