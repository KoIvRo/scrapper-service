import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from models.dto.schemas import Link, GlobalLink, PaginatedLink
from services.link_service import LinkService
from cache_manager import CacheManager
from exceptions import (
    UnknownChatError,
    ExistLink,
    InvalidLimit,
    InvalidPage,
    UnknownLink,
)


@pytest.fixture
def mock_cache():
    """Мок CacheManager."""
    cache = MagicMock(spec=CacheManager)
    cache.get_cache_links = AsyncMock(return_value=None)
    cache.save_cache_links = AsyncMock()
    cache.delete_cache_links = AsyncMock()
    return cache


@pytest.fixture
def link_service(mock_repo, mock_validator, mock_cache):
    """Фикстура сервиса ссылок с моком кэша."""
    return LinkService(
        repo=mock_repo, cache_manager=mock_cache, validators=[mock_validator]
    )


class TestLinkService:
    """Тестирование LinkService."""

    @pytest.mark.asyncio
    async def test_add_link(
        self, link_service, sample_link_data, mock_repo, mock_cache
    ):
        """Добавление ссылки через сервис."""
        chat_id = sample_link_data["chat_id"]
        url = str(sample_link_data["url"])
        tags = sample_link_data["tags"]

        mock_repo.exist_chat.return_value = True
        mock_repo.exist_link.return_value = False
        mock_repo.append_link.return_value = Link(
            id=1, chat_id=chat_id, url=url, tags=tags
        )

        await link_service.append_chat(chat_id)
        result = await link_service.append_link(chat_id=chat_id, url=url, tags=tags)

        assert str(result.url) == url
        assert result.tags == tags
        mock_repo.append_link.assert_called_once_with(chat_id, url, tags)
        mock_cache.delete_cache_links.assert_called_once_with(chat_id)

    @pytest.mark.asyncio
    async def test_get_user_links_with_tag_filter(
        self, link_service, sample_link_data, mock_repo, mock_cache
    ):
        """Фильтрация ссылок по тегу."""
        chat_id = sample_link_data["chat_id"]
        url = str(sample_link_data["url"])
        tags = sample_link_data["tags"]

        expected_link = Link(id=1, chat_id=chat_id, url=url, tags=tags)
        paginated_links = PaginatedLink(items=[expected_link], has_next=False)

        mock_repo.exist_chat.return_value = True
        mock_repo.get_chat_links_paginated.return_value = paginated_links

        result = await link_service.get_user_links_paginated(
            chat_id=chat_id, page=0, limit=5
        )

        assert len(result.items) == 1
        assert str(result.items[0].url) == url
        assert result.items[0].tags == tags
        mock_repo.get_chat_links_paginated.assert_called_once_with(chat_id, 0, 5)
        mock_cache.get_cache_links.assert_called_once_with(chat_id, 0, 5)
        mock_cache.save_cache_links.assert_called_once_with(
            chat_id, 0, 5, paginated_links
        )

    @pytest.mark.asyncio
    async def test_get_user_links_from_cache(
        self, link_service, sample_link_data, mock_repo, mock_cache
    ):
        """Получение ссылок из кэша."""
        chat_id = sample_link_data["chat_id"]
        url = str(sample_link_data["url"])
        tags = sample_link_data["tags"]

        expected_link = Link(id=1, chat_id=chat_id, url=url, tags=tags)
        paginated_links = PaginatedLink(items=[expected_link], has_next=False)

        mock_repo.exist_chat.return_value = True
        mock_cache.get_cache_links.return_value = paginated_links

        result = await link_service.get_user_links_paginated(
            chat_id=chat_id, page=0, limit=5
        )

        assert len(result.items) == 1
        assert str(result.items[0].url) == url
        mock_cache.get_cache_links.assert_called_once_with(chat_id, 0, 5)
        mock_repo.get_chat_links_paginated.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_link(
        self, link_service, sample_link_data, mock_repo, mock_cache
    ):
        """Удаление ссылки через сервис."""
        chat_id = sample_link_data["chat_id"]
        url = str(sample_link_data["url"])
        tags = sample_link_data["tags"]

        deleted_link = Link(id=1, chat_id=chat_id, url=url, tags=tags)

        mock_repo.exist_link.return_value = True
        mock_repo.delete_link.return_value = deleted_link

        result = await link_service.delete_link(chat_id=chat_id, url=url)

        assert str(result.url) == url
        mock_repo.delete_link.assert_called_once_with(chat_id, url)
        mock_cache.delete_cache_links.assert_called_once_with(chat_id)

    @pytest.mark.asyncio
    async def test_get_all_links_for_scheduler(
        self, link_service, sample_link_data, mock_repo
    ):
        """Получение всех ссылок для планировщика."""
        url = str(sample_link_data["url"])

        expected_link = GlobalLink(id=1, url=url, updated_at=datetime.now())
        paginated_links = PaginatedLink(items=[expected_link], has_next=False)

        mock_repo.get_all_links_paginated.return_value = paginated_links

        result = await link_service.get_all_links_paginated(page=0, limit=100)

        assert len(result.items) == 1
        assert str(result.items[0].url) == url
        mock_repo.get_all_links_paginated.assert_called_once_with(0, 100)

    @pytest.mark.asyncio
    async def test_add_link_duplicate_error(
        self, link_service, sample_link_data, mock_repo
    ):
        """Ошибка при добавлении существующей ссылки."""
        chat_id = sample_link_data["chat_id"]
        url = str(sample_link_data["url"])
        tags = sample_link_data["tags"]

        mock_repo.exist_chat.return_value = True
        mock_repo.exist_link.return_value = True

        with pytest.raises(ExistLink):
            await link_service.append_link(chat_id=chat_id, url=url, tags=tags)

    @pytest.mark.asyncio
    async def test_get_links_invalid_page(self, link_service, mock_repo):
        """Ошибка при невалидном номере страницы."""
        with pytest.raises(InvalidPage):
            await link_service.get_user_links_paginated(chat_id=123, page=-1, limit=5)

    @pytest.mark.asyncio
    async def test_get_links_invalid_limit(self, link_service, mock_repo):
        """Ошибка при невалидном лимите."""
        with pytest.raises(InvalidLimit):
            await link_service.get_user_links_paginated(chat_id=123, page=0, limit=0)

        with pytest.raises(InvalidLimit):
            await link_service.get_user_links_paginated(chat_id=123, page=0, limit=101)

    @pytest.mark.asyncio
    async def test_get_links_unknown_chat(self, link_service, mock_repo):
        """Ошибка при получении ссылок несуществующего чата."""
        mock_repo.exist_chat.return_value = False

        with pytest.raises(UnknownChatError):
            await link_service.get_user_links_paginated(chat_id=999, page=0, limit=5)

    @pytest.mark.asyncio
    async def test_delete_link_unknown(self, link_service, sample_link_data, mock_repo):
        """Ошибка при удалении несуществующей ссылки."""
        chat_id = sample_link_data["chat_id"]
        url = str(sample_link_data["url"])

        mock_repo.exist_link.return_value = False

        with pytest.raises(UnknownLink):
            await link_service.delete_link(chat_id=chat_id, url=url)
