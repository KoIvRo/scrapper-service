import os
import sys
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).parent.parent / "src"))

os.environ["BOT_TOKEN"] = "test_token"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_password"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["SCRAPPER_URL"] = "http://localhost:8001"
os.environ["GITHUB_TOKEN"] = "test_github_token"

from pydantic import HttpUrl
from models.dto.schemas import Link
from main import app
from services.link_service import LinkService
from dependencies.notifier_factory import NotifierFactory
from validators.validators import (
    GitHubUrlValidator,
    StackOverFlowUrlValidator,
    BaseUrlValidator,
)
from repository.base_repository import BaseRepository
from clients.stackoverflow_client import StackOverFlowClient
from clients.github_client import GitHubClient
from dependencies.client_factory import ClientFactory


@pytest.fixture
def sample_global_link():
    """Пример глобальной ссылки."""
    return type(
        "GlobalLink",
        (),
        {
            "id": 1,
            "url": HttpUrl("https://stackoverflow.com/questions/79901927"),
            "updated_at": None,
        },
    )


@pytest.fixture
def mock_service():
    """Мок сервиса."""
    service = MagicMock()
    service.get_all_links_paginated = AsyncMock()
    service.get_chats_for_link = AsyncMock()
    service.update_link_timestamp = AsyncMock()
    return service


@pytest.fixture
def mock_client():
    """Мок клиента."""
    client = AsyncMock()
    client.validate_url = MagicMock()
    client.get_last_update = AsyncMock()
    return client


@pytest.fixture
def mock_notifier():
    """Мок нотифаера."""
    notifier = AsyncMock()
    notifier.notify = AsyncMock()
    return notifier


@pytest.fixture
def mock_repo():
    """Мок репозитория."""
    repo = MagicMock(spec=BaseRepository)
    repo.append_chat = AsyncMock()
    repo.delete_chat = AsyncMock()
    repo.exist_chat = AsyncMock()
    repo.exist_link = AsyncMock()
    repo.get_chat_links_paginated = AsyncMock()
    repo.get_all_links_paginated = AsyncMock()
    repo.get_chats_for_link = AsyncMock()
    repo.update_link_timestamp = AsyncMock()
    repo.append_link = AsyncMock()
    repo.delete_link = AsyncMock()
    return repo


@pytest.fixture
def mock_validator():
    """Мок валидатора URL."""
    validator = MagicMock(spec=BaseUrlValidator)
    validator.validate_url = MagicMock(return_value=True)
    return validator


@pytest.fixture
def link_service(mock_repo, mock_validator):
    """Фикстура сервиса ссылок."""
    return LinkService(repo=mock_repo, validators=[mock_validator])


@pytest.fixture
def another_link():
    """Пример ссылки."""
    return Link(
        id=2,
        url="https://stackoverflow.com/questions/123",
        chat_id=456,
        tags=[],
        updated_at=datetime(2024, 1, 1, 11, 0, 0),
    )


@pytest.fixture
def sample_link():
    """Пример ссылки."""
    return Link(
        id=1,
        url="https://github.com/user/repo",
        chat_id=123,
        tags=["work"],
        updated_at=datetime(2024, 1, 1, 10, 0, 0),
    )


@pytest.fixture
def client_factory():
    """Фикстура фабрики клиентов."""
    factory = ClientFactory()
    factory._github_client = None
    factory._stackoverflow_client = None
    return factory


@pytest.fixture
def notifier_factory():
    """Фикстура фабрики нотифаеров."""
    factory = NotifierFactory()
    factory._notifier = None
    return factory


@pytest.fixture
def sample_link_data():
    """Пример данных ссылки."""
    return {
        "chat_id": 123,
        "url": HttpUrl("https://github.com/user/repo"),
        "tags": ["work", "python"],
    }


@pytest.fixture
def github_token():
    """Токен GitHub."""
    return "test_github_token"


@pytest.fixture
def github_client(github_token):
    """Клиент GitHub."""
    return GitHubClient(github_token, GitHubUrlValidator)


@pytest.fixture
def stackoverflow_client():
    """Клиент StackOverflow."""
    return StackOverFlowClient(StackOverFlowUrlValidator)


@pytest.fixture
def mock_httpx_client():
    """Мок HTTPX клиента."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    return mock_client


@pytest.fixture
def sample_github_url():
    """Пример GitHub URL."""
    return "https://github.com/owner/repo"


@pytest.fixture
def sample_github_response():
    """Пример ответа GitHub API."""
    return {
        "id": 123456,
        "name": "repo",
        "full_name": "owner/repo",
        "updated_at": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def client():
    """FastAPI тестовый клиент."""
    return TestClient(app)


@pytest.fixture
def valid_github_link():
    """Валидная GitHub ссылка для запроса."""
    return {
        "chat_id": 123,
        "url": "https://github.com/user/repo",
        "tags": ["work", "python"],
    }
