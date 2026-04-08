import httpx
from typing import Optional
from abc import ABC, abstractmethod
from validators.validators import BaseUrlValidator
from models.dto.schemas import BaseEvent


class BaseClient(ABC):
    """Интерфейс для клиентов."""

    def __init__(
        self, base_url: str, validator: BaseUrlValidator, timeout: int = 10
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self._validator = validator
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Получение клиента."""

        if self._client:
            return self._client

        self._client = httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, follow_redirects=True
        )

        return self._client

    @abstractmethod
    async def get_last_event(self, url: str) -> Optional[BaseEvent]:
        """Получение времени последнего апдейта."""
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Проверки валидности ссылки."""
        pass
