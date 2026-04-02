from typing import Optional
from abc import ABC, abstractmethod
from models.schemas import ListLinksResponse


class BaseClient(ABC):
    """Интерфейс клиента."""

    def __init__(self, base_url: str):
        pass

    @abstractmethod
    async def get_links(self, chat_id: int, page: int, limit: int) -> ListLinksResponse:
        """Получение всех ссылок."""
        pass

    @abstractmethod
    async def register_chat(self, chat_id: int) -> bool:
        """Регистрация чата."""
        pass

    @abstractmethod
    async def delete_chat(self, chat_id: int) -> bool:
        """Удаление чата."""
        pass

    @abstractmethod
    async def append_link(self, chat_id: int, url: str, tags: Optional[str]) -> bool:
        """Добавление ссылки."""
        pass

    @abstractmethod
    async def delete_link(self, chat_id: int, url: str) -> bool:
        """Удаление ссылки."""
        pass
