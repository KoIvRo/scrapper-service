from typing import Optional
from models.dto.schemas import Link, GlobalLink, PaginatedLink
from .base_service import BaseService
from validators.validators import BaseUrlValidator
from repository.base_repository import BaseRepository
from exceptions import (
    UnknownChatError,
    UnknownLink,
    ExistLink,
    InvalidURL,
    InvalidLimit,
    InvalidPage,
)
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class LinkService(BaseService):
    """Прокси к слою базы данных."""

    def __init__(
        self, repo: BaseRepository, validators: list[BaseUrlValidator]
    ) -> None:
        self._repo = repo
        self._validators = validators

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

        return await self._repo.get_chat_links_paginated(chat_id, page, limit)

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

        if not self._validate_url(url):
            logger.warning("Attempt to add invalid url", extra={"url": url})
            raise InvalidURL(url)

        if await self._exist_link(chat_id, url):
            logger.warning(
                "Attempt to add existing url", extra={"url": url, "chat_id": chat_id}
            )
            raise ExistLink(url)

        return await self._repo.append_link(chat_id, url, tags)

    async def delete_link(self, chat_id: int, url: str) -> Link:
        """Удаление ссылки"""

        if not await self._exist_link(chat_id, url):
            logger.warning("Attempt to delete non-existent url", extra={"url": url})
            raise UnknownLink(url)

        return await self._repo.delete_link(chat_id, url)

    async def get_chats_for_link(self, link_id: int) -> bool:
        """Получение чатов, отслеживающих ссылку."""

        return await self._repo.get_chats_for_link(link_id)

    async def update_link_timestamp(self, link_id, timestamp: datetime) -> None:
        """Обновить время ссылки."""

        await self._repo.update_link_timestamp(link_id, timestamp)

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
