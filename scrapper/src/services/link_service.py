from asyncio import Lock
from typing import Optional
from models.dto.schemas import Link, GlobalLink, PaginatedLink, LinkUpdate
from .base_service import BaseService
from validators.validators import BaseUrlValidator
from repository.base_repository import BaseRepository
from cache_manager import CacheManager
from exceptions import (
    UnknownChatError,
    UnknownLink,
    ExistLink,
    InvalidURL,
    InvalidLimit,
    InvalidPage,
)
from datetime import datetime
from metrics import links_on_track
import logging


logger = logging.getLogger(__name__)


class LinkService(BaseService):
    """Прокси к слою базы данных."""

    def __init__(
        self,
        repo: BaseRepository,
        cache_manager: CacheManager,
        validators: list[BaseUrlValidator],
    ) -> None:
        self._repo = repo
        self._cache_manager = cache_manager
        self._validators = validators
        self._lock = Lock()

    async def get_user_links_paginated(
        self, chat_id: int, page: int, limit: int
    ) -> PaginatedLink[Link]:
        """Получение списка ссылок пагинированно."""

        if not await self._exist_chat(chat_id):
            logger.warning(
                "Attempt to take links from a non-existent chat",
                extra={"chat_id": chat_id},
            )
            raise UnknownChatError(chat_id)

        self._validate_pagination(page, limit)

        paginated_link = await self._cache_manager.get_cache_links(chat_id, page, limit)

        if paginated_link is None:
            paginated_link = await self._repo.get_chat_links_paginated(
                chat_id, page, limit
            )
            await self._cache_manager.save_cache_links(
                chat_id, page, limit, paginated_link
            )

        return paginated_link

    async def get_all_links_paginated(
        self, page: int, limit: int
    ) -> PaginatedLink[GlobalLink]:
        """Получить пагинированные ссылки и есть ли остаток."""

        self._validate_pagination(page, limit)

        return await self._repo.get_all_links_paginated(page, limit)

    async def append_chat(self, chat_id: int) -> None:
        """Добавить чат."""

        await self._repo.append_chat(chat_id)

    async def delete_chat(self, chat_id: int) -> None:
        """Удалить чат."""
        async with self._lock:
            if not (await self._exist_chat(chat_id)):
                logger.warning(
                    "Attempt to delete non-existent chat", extra={"chat_id": chat_id}
                )
                raise UnknownChatError(chat_id)

            await self._repo.delete_chat(chat_id)

    async def append_link(
        self, chat_id: int, url: str, tags: Optional[list[str]]
    ) -> Link:
        """Добавление ссылки."""
        async with self._lock:
            if not self._validate_url(url):
                logger.warning("Attempt to add invalid url", extra={"url": url})
                raise InvalidURL(url)

            if await self._exist_link(chat_id, url):
                logger.warning(
                    "Attempt to add existing url",
                    extra={"url": url, "chat_id": chat_id},
                )
                raise ExistLink(url)

            await self._cache_manager.delete_cache_links(chat_id)

            link = await self._repo.append_link(chat_id, url, tags)

            source = "github" if "github.com" in url else "stackoverflow"
            links_on_track.labels(tracked_source=source).inc()

            return link

    async def delete_link(self, chat_id: int, url: str) -> Link:
        """Удаление ссылки"""
        async with self._lock:
            if not await self._exist_link(chat_id, url):
                logger.warning("Attempt to delete non-existent url", extra={"url": url})
                raise UnknownLink(url)

            await self._cache_manager.delete_cache_links(chat_id)

            link = await self._repo.delete_link(chat_id, url)

            source = "github" if "github.com" in url else "stackoverflow"
            links_on_track.labels(tracked_source=source).dec()

            return link

    async def get_chats_for_link(self, link_id: int) -> bool:
        """Получение чатов, отслеживающих ссылку."""

        async with self._lock:
            return await self._repo.get_chats_for_link(link_id)

    async def update_link_timestamp(self, link_id, timestamp: datetime) -> None:
        """Обновить время ссылки."""

        await self._repo.update_link_timestamp(link_id, timestamp)

    async def save_update_outbox(
        self, link_id: int, timestamp: datetime, update: LinkUpdate
    ):
        """Сохранить обновление в outbox."""
        await self._repo.save_update_outbox(link_id, timestamp, update)
        logger.info("Updates saved in outbox")

    async def get_outbox_updates(self, limit: int) -> Optional[list[LinkUpdate]]:
        """Получить ожидающиеся обновления."""
        result = await self._repo.get_outbox_updates(limit)
        if result:
            logger.info("Received updates from outbox", extra={"count": len(result)})
            return result
        return None

    async def mark_outbox_updates(self, updates: list[LinkUpdate]) -> None:
        """Пометить обновления обработанными."""
        # ЭТО id В ТАБЛИЦЕ OUTBOX!!!
        await self._repo.mark_outbox_updates([update.id for update in updates])

    async def cleanup_outbox(self, days_to_truncate: int) -> None:
        """Очистить старые сообщения в outbox."""
        await self._repo.cleanup_outbox(days_to_truncate)

    def _validate_url(self, url: str) -> bool:
        """Проверить по всем валидаторам при добавлении."""

        return any(validator.validate_url(url) for validator in self._validators)

    async def _exist_link(self, chat_id: int, url: str) -> bool:
        """Проверка на дубликат."""

        return await self._repo.exist_link(chat_id, url)

    async def _exist_chat(self, chat_id: int) -> bool:
        """Проверка существует ли чат."""

        return await self._repo.exist_chat(chat_id)

    def _validate_pagination(self, page: int, limit: int) -> None:
        """Валидируем пагинацию."""
        if not self._validate_page(page):
            logger.warning("Invalid page format", extra={"page": page})
            raise InvalidPage(page)

        if not self._validate_limit(limit):
            logger.warning("Invalid limit format", extra={"limit": limit})
            raise InvalidLimit(limit)

    @staticmethod
    def _validate_page(page: int) -> bool:
        """Валидация старницы."""
        return page >= 0

    @staticmethod
    def _validate_limit(limit: int) -> bool:
        """Валидация количества ссылок."""
        max_limit = 100
        return 0 < limit <= max_limit
