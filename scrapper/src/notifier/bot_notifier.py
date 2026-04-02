import httpx
from typing import Optional
from .base_notifier import BaseNotifier
from models.dto.schemas import LinkUpdate
from logger_config import setup_logger


logger = setup_logger(__name__)


class BotNotifier(BaseNotifier):
    """Уведомление бота по REST API."""

    def __init__(self, bot_url: str, timeout: int = 5) -> None:
        self._bot_url = bot_url
        self._client: Optional[httpx.AsyncClient] = None
        self._timeout = timeout

    async def _get_client(self) -> httpx.AsyncClient:
        """Получение клиента."""

        if not self._client:
            self._client = httpx.AsyncClient(timeout=self._timeout)

        return self._client

    async def notify(self, links_updates: list[LinkUpdate]) -> None:
        """Оповещение."""

        for link_update in links_updates:
            await self._send_request(link_update)

    async def _send_request(self, link_update: LinkUpdate) -> None:
        """Отсылка боту."""

        client = await self._get_client()

        await client.post(f"{self._bot_url}/updates", json=link_update.model_dump())

        logger.info(f"Отправлено уведомлние о обновлении ссылки: {link_update.url}")
