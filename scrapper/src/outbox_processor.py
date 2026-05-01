import asyncio
from services.base_service import BaseService
from notifier.base_notifier import BaseNotifier
from config import settings
import logging

logger = logging.getLogger(__name__)


class OutboxProcessor:
    """Проверка ссылок в таблице Outbox."""

    def __init__(
        self,
        service: BaseService,
        notifier: BaseNotifier,
        batch_size: int = settings.batch_size,
        update_time: int = 1,
    ) -> None:
        self._service = service
        self._notifier = notifier
        self._batch_size = batch_size
        self._update_time = update_time
        self._running: bool = False

    async def start(self) -> None:
        """Начать работу по проверке Outbox."""

        self._running = True

        while self._running:
            try:
                start = asyncio.get_running_loop().time()

                await self._check_all_links()

                elapsed = asyncio.get_running_loop().time() - start

                await asyncio.sleep(max(0, self._update_time - elapsed))
            except Exception as e:
                logger.critical("Error in OutboxProcessor", extra={"error": e})
                await asyncio.sleep(self._update_time)

    async def _check_all_links(self) -> None:
        """Проверить все ссылки."""

        updates = await self._service.get_outbox_updates(self._batch_size)

        if updates:
            logger.info("Have updates", extra={"count": len(updates)})
            await self._notifier.notify(updates)
            await self._service.mark_outbox_updates(updates)
            logger.info("Sent updates", extra={"count": len(updates)})

    async def stop(self) -> None:
        """Остановка работы OutboxProcessor."""
        self.running = False
