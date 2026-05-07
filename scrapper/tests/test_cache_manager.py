import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from models.dto.schemas import Link, PaginatedLink
from cache_manager import CacheManager


@pytest.fixture
def mock_redis():
    """Мок для Redis клиента."""
    with patch("cache_manager.Redis") as mock:
        redis_instance = MagicMock()
        redis_instance.get = AsyncMock(return_value=None)
        redis_instance.set = AsyncMock()
        redis_instance.expire = AsyncMock()
        redis_instance.keys = AsyncMock(return_value=[])
        redis_instance.delete = AsyncMock()
        mock.return_value = redis_instance
        yield redis_instance


@pytest.fixture
def cache_manager(mock_redis):
    """Экземпляр CacheManager с замоканным Redis."""
    return CacheManager(host="localhost", port=6379, ttl=300)


@pytest.fixture
def sample_paginated_link():
    """Тестовые данные."""
    links = [
        Link(
            id=1,
            url="https://github.com/user/repo",
            chat_id=123,
            tags=["work"],
        ),
        Link(
            id=2,
            url="https://github.com/user/repo2",
            chat_id=123,
            tags=["test"],
        ),
    ]
    return PaginatedLink(items=links, has_next=False)


class TestCacheManager:
    """Тесты для CacheManager."""

    @pytest.mark.asyncio
    async def test_get_miss(self, cache_manager, mock_redis):
        """Промах кэша — возвращает None."""
        result = await cache_manager.get_cache_links(chat_id=123, page=0, limit=5)
        assert result is None

    @pytest.mark.asyncio
    async def test_save_and_get(self, cache_manager, mock_redis, sample_paginated_link):
        """Сохраняем и тут же получаем из локального кэша."""
        await cache_manager.save_cache_links(123, 0, 5, sample_paginated_link)

        result = await cache_manager.get_cache_links(chat_id=123, page=0, limit=5)

        assert result is not None
        assert len(result.items) == 2
        assert str(result.items[0].url) == "https://github.com/user/repo"
        assert result.has_next is False
        mock_redis.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_from_valkey(
        self, cache_manager, mock_redis, sample_paginated_link
    ):
        """Получаем из Valkey когда локальный кэш пуст."""
        json_data = json.dumps(
            {
                "items": [
                    {
                        "id": 1,
                        "url": "https://github.com/user/repo",
                        "chat_id": 123,
                        "tags": ["work"],
                    },
                    {
                        "id": 2,
                        "url": "https://github.com/user/repo2",
                        "chat_id": 123,
                        "tags": ["test"],
                    },
                ],
                "has_next": False,
            }
        )
        mock_redis.get.return_value = json_data

        result = await cache_manager.get_cache_links(chat_id=123, page=0, limit=5)

        assert result is not None
        assert len(result.items) == 2
        mock_redis.get.assert_called_once_with("links:123:0:5")

    @pytest.mark.asyncio
    async def test_save_calls_valkey(
        self, cache_manager, mock_redis, sample_paginated_link
    ):
        """Сохранение пишет в Valkey."""
        await cache_manager.save_cache_links(123, 0, 5, sample_paginated_link)

        mock_redis.set.assert_called_once()
        mock_redis.expire.assert_called_once()
        call_args = mock_redis.set.call_args[0]
        assert call_args[0] == "links:123:0:5"

    @pytest.mark.asyncio
    async def test_delete_cache(self, cache_manager, mock_redis, sample_paginated_link):
        """Удаление чистит локальный кэш и Valkey."""
        await cache_manager.save_cache_links(123, 0, 5, sample_paginated_link)

        mock_redis.keys.return_value = ["links:123:0:5", "links:123:1:5"]
        await cache_manager.delete_cache_links(123)

        assert len(cache_manager._cache) == 0
        mock_redis.delete.assert_called_once_with("links:123:0:5", "links:123:1:5")

    @pytest.mark.asyncio
    async def test_delete_cache_no_keys(self, cache_manager, mock_redis):
        """Удаление когда ключей нет — не падает."""
        mock_redis.keys.return_value = []
        await cache_manager.delete_cache_links(123)
        mock_redis.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_local_cache_hit_no_valkey_call(
        self, cache_manager, mock_redis, sample_paginated_link
    ):
        """Повторный запрос не дёргает Valkey."""
        await cache_manager.save_cache_links(123, 0, 5, sample_paginated_link)

        result1 = await cache_manager.get_cache_links(123, 0, 5)

        result2 = await cache_manager.get_cache_links(123, 0, 5)

        assert result1 is not None
        assert result2 is not None
        mock_redis.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_different_keys(
        self, cache_manager, mock_redis, sample_paginated_link
    ):
        """Разные ключи независимы."""
        await cache_manager.save_cache_links(123, 0, 5, sample_paginated_link)

        result = await cache_manager.get_cache_links(999, 0, 5)
        assert result is None
        result = await cache_manager.get_cache_links(123, 1, 5)
        assert result is None

    @pytest.mark.asyncio
    async def test_valkey_error_returns_none(self, cache_manager, mock_redis):
        """Ошибка Valkey не ломает get."""
        mock_redis.get.side_effect = Exception("Connection refused")
        result = await cache_manager.get_cache_links(123, 0, 5)
        assert result is None

    @pytest.mark.asyncio
    async def test_valkey_error_on_save_not_raise(
        self, cache_manager, mock_redis, sample_paginated_link
    ):
        """Ошибка Valkey не ломает save."""
        mock_redis.set.side_effect = Exception("Connection refused")
        await cache_manager.save_cache_links(123, 0, 5, sample_paginated_link)

    @pytest.mark.asyncio
    async def test_valkey_error_on_delete_not_raise(self, cache_manager, mock_redis):
        """Ошибка Valkey не ломает delete."""
        mock_redis.keys.side_effect = Exception("Connection refused")
        await cache_manager.delete_cache_links(123)
