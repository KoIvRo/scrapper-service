import httpx
from typing import Optional
from abc import ABC, abstractmethod
from validators.validators import BaseUrlValidator
from models.dto.schemas import BaseEvent
from .retry_decorator import retry_decorator


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

    @retry_decorator
    async def _get(
        self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None
    ) -> httpx.Response:
        """Сделать get."""
        client = await self._get_client()
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    @abstractmethod
    async def get_last_event(self, url: str) -> Optional[BaseEvent]:
        """Получение последнего апдейта."""
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Проверки валидности ссылки."""
        pass
