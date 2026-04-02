from models.dto.schemas import Link, GlobalLink, PaginatedLink
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from exceptions import DataBaseError
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


def db_error_handler(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Data Base error", extra={"error": e})
            raise DataBaseError(e) from e

    return wrapper


class BaseRepository(ABC):
    """Интерфейс для классов хранения данных."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    async def get_all_chats(self) -> set[int]:
        """Получить все чаты."""
        pass

    @abstractmethod
    async def get_all_links_paginated(
        self, page: int, limit: int
    ) -> PaginatedLink[GlobalLink]:
        """Получить все ссылки пагинированно."""
        pass

    @abstractmethod
    async def append_chat(self, chat_id: int) -> None:
        """Добавление чата."""
        pass

    @abstractmethod
    async def delete_chat(self, chat_id: int) -> None:
        """Удаление чата."""
        pass

    @abstractmethod
    async def get_chat_links_paginated(
        self, chat_id: int, page: int, limit: int
    ) -> PaginatedLink[Link]:
        """Получить все ссылки юзера с пагинацией."""
        pass

    @abstractmethod
    async def append_link(self, chat_id: int, url: str, tags: list[str]) -> Link:
        """Добавить отслеживаемую ссылку."""
        pass

    @abstractmethod
    async def delete_link(self, chat_id: int, url: str) -> Link:
        """Удалить отслеживаемую ссылку."""
        pass

    @abstractmethod
    async def get_chats_for_link(self, link_id: int) -> list[int]:
        """Получение чатов отслеживающих ссылку."""
        pass

    @abstractmethod
    async def update_link_timestamp(self, link_id: int, cur_date: datetime) -> None:
        """Обновление времени у ссылки."""
        pass

    @abstractmethod
    async def exist_link(self, chat_id: int, url: str) -> bool:
        """Проверка существует ли ссылка."""
        pass

    @abstractmethod
    async def exist_chat(self, chat_id: int) -> bool:
        """Проверка существует ли чат."""
        pass
