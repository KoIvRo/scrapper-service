from typing import Optional
from models.dto.schemas import Link, GlobalLink, PaginatedLink
from abc import ABC, abstractmethod
from validators.validators import BaseUrlValidator
from repository.base_repository import BaseRepository
from datetime import datetime


class BaseService(ABC):
    """Базовый класс для сервиса."""

    def __init__(self, repo: BaseRepository, validators: list[BaseUrlValidator]):
        pass

    @abstractmethod
    async def get_user_links_paginated(
        self, chat_id: int, page: int, limit: int
    ) -> PaginatedLink[Link]:
        """Получение ссылок юзера пагинированно."""
        pass

    @abstractmethod
    async def get_all_links_paginated(
        self, page: int, limit: int
    ) -> PaginatedLink[GlobalLink]:
        """Получение всех ссылок с пагинацией. Вовзращает ссылки и есть ли еще."""
        pass

    @abstractmethod
    async def append_chat(self, chat_id: int) -> None:
        """Добавить чат."""
        pass

    @abstractmethod
    async def delete_chat(self, chat_id: int) -> None:
        """Удалить чат."""
        pass

    @abstractmethod
    async def append_link(
        self, chat_id: int, url: str, tags: Optional[list[str]]
    ) -> Link:
        """Добавление ссылки."""
        pass

    @abstractmethod
    async def delete_link(self, chat_id: int, url: str) -> Link:
        """Удаление ссылки"""
        pass

    @abstractmethod
    async def get_chats_for_link(self, link_id: int) -> bool:
        """Получение чатов, отслеживающих ссылку."""
        pass

    @abstractmethod
    async def update_link_timestamp(self, link_id, timestamp: datetime) -> None:
        """Обновить время ссылки."""
        pass
