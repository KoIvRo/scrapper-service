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
        base_notifier: BaseNotifier,
        #reserve_notifier: BaseNotifier,
        batch_size: int = settings.concurrency.batch_size,
        update_time: int = settings.outbox.update_time,
        cleanup_interval: int = settings.outbox.cleanup_interval,
        days_to_truncate: int = settings.outbox.days_to_truncate,
    ) -> None:
        self._service = service
        self._base_notifier = base_notifier
        #self._reserve_notifier = reserve_notifier
        self._batch_size = batch_size
        self._update_time = update_time
        self._running: bool = False
        self._cleanup_interval = cleanup_interval
        self._days_to_truncate = days_to_truncate

    async def start(self) -> None:
        """Начать работу по проверке Outbox."""

        self._running = True
        last_cleanup = asyncio.get_running_loop().time()

        while self._running:
            try:
                start = asyncio.get_running_loop().time()

                if start - last_cleanup > self._cleanup_interval:
                    last_cleanup = start
                    await self._service.cleanup_outbox(self._days_to_truncate)
                    logger.info("Outbox was cleaned")

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

            """Код использовался когда http был запасным транспортом."""
            # try:
            #     await self._base_notifier.notify(updates)
            # except Exception as e:
            #     logger.warning("HTTP failed", extra={"error": e})
            #     try:
            #         await self._reserve_notifier.notify(updates)
            #     except Exception as e:
            #         logger.warning("Kafka failed", extra={"error": e})
            #         return None


            try:
                await self._base_notifier.notify(updates)
            except Exception as e:
                logger.warning("Kafka failed", extra={"error": e})
                return None


            await self._service.mark_outbox_updates(updates)
            logger.info("Sent updates", extra={"count": len(updates)})

    async def stop(self) -> None:
        """Остановка работы OutboxProcessor."""
        self._running = False
