import httpx
from aiobreaker import CircuitBreaker
from typing import Optional
from abc import ABC, abstractmethod
from validators.validators import BaseUrlValidator
from models.dto.schemas import BaseEvent
from retry_decorator import retry_decorator
from metrics import request_duration
import time


class BaseClient(ABC):
    """Интерфейс для клиентов."""

    def __init__(
        self,
        base_url: str,
        validator: BaseUrlValidator,
        timeout: httpx.Timeout,
        cb: CircuitBreaker,
    ) -> None:
        self.base_url = base_url
        self._timeout = timeout
        self._validator = validator
        self._client: Optional[httpx.AsyncClient] = None
        self._cb: CircuitBreaker = cb

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

        start = time.monotonic()

        response = await client.get(url, params=params, headers=headers)

        duration_ms = (time.monotonic() - start) * 1000
        request_duration.labels(
            scope="external_source", scope_type=self.__class__.__name__
        ).observe(duration_ms)

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
