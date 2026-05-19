import httpx
from typing import Optional
from aiobreaker import CircuitBreaker
from .base_notifier import BaseNotifier
from models.dto.schemas import LinkUpdate
from retry_decorator import retry_decorator
from config import settings
import logging


logger = logging.getLogger(__name__)


class HTTPNotifier(BaseNotifier):
    """Уведомление бота по REST API."""

    def __init__(self, bot_url: str, cb: CircuitBreaker) -> None:
        self._bot_url = bot_url
        self._client: Optional[httpx.AsyncClient] = None
        self._cb = cb

    async def _get_client(self) -> httpx.AsyncClient:
        """Получение клиента."""

        if not self._client:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(
            connect=settings.timeout_connect,
            read=settings.timeout_read,
            write=settings.timeout_write,
            pool=settings.timeout_pool,
        ))

        return self._client

    async def notify(self, links_updates: list[LinkUpdate]) -> None:
        """Оповещение."""

        for link_update in links_updates:
            await self._cb.call_async(
                self._send_request,
                link_update,
            )

    @retry_decorator
    async def _send_request(self, link_update: LinkUpdate) -> None:
        """Отсылка боту."""

        client = await self._get_client()

        response = await client.post(
            f"{self._bot_url}/updates", json=link_update.model_dump()
        )

        response.raise_for_status()

        logger.info("Link update notification sent", extra={"url": link_update.url})
