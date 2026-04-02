import sys
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).parent.parent / "src"))
os.environ["BOT_TOKEN"] = "test_token"

from config import settings  # noqa


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
def client():
    """Тестовый клиент FastAPI с подставленным токеном."""
    with patch.dict("os.environ", {"BOT_TOKEN": "test_token"}):
        from main import app

        return TestClient(app)


@pytest.fixture
def valid_update_data():
    """Корректные данные для обновления."""
    return {
        "id": 1,
        "url": "https://github.com/user/repo",
        "description": "Test update",
        "tgChatIds": [123, 456],
    }


@pytest.fixture
def mock_bot():
    """Мок для бота."""
    with patch("api.updates.get_bot") as mock:
        bot = AsyncMock()
        bot.send_message = AsyncMock()
        mock.return_value = bot
        yield mock
