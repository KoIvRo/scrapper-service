import httpx
from typing import Optional
from abc import ABC, abstractmethod
from validators.validators import BaseUrlValidator
from models.dto.schemas import BaseEvent


class BaseClient(ABC):
    """Интерфейс для клиентов."""

    def __init__(
        self, base_url: str, validator: BaseUrlValidator, timeout: httpx.Timeout
    ) -> None:
        self.base_url = base_url
        self._timeout = timeout
        self._validator = validator
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client and not self._client.is_closed:
            return self._client

        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,
        )
        return self._client

    @abstractmethod
    async def get_last_event(self, url: str) -> Optional[BaseEvent]:
        """Получение последнего апдейта."""
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Проверки валидности ссылки."""
        pass
