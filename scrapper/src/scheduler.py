import asyncio
from typing import Optional
from datetime import datetime
from clients.base_client import BaseClient
from services.base_service import BaseService
from notifier.base_notifier import BaseNotifier
from models.dto.schemas import GlobalLink, LinkUpdate, PaginatedLink, LinkEvent
import logging

logger = logging.getLogger(__name__)


class Scheduler:
    """Планировщик проверки ссылок."""

    def __init__(
        self,
        service: BaseService,
        clients: list[BaseClient],
        notifier: BaseNotifier,
        update_time: int = 10,
        batch_size: int = 100,
        concurrency: int = 20,
    ) -> None:
        self._service = service
        self._clients = clients
        self._notifier = notifier
        self._running = False
        self._update_time = update_time
        self._batch_size = batch_size
        self._sem = asyncio.Semaphore(concurrency)

    async def start(self) -> None:
        """Запуск"""
        self._running = True

        logger.info("Scheduler started.")

        while self._running:
            try:
                start = asyncio.get_running_loop().time()

                await self._check_all_links()

                elapsed = asyncio.get_event_loop().time() - start
                await asyncio.sleep(max(0, self._update_time - elapsed))
            except Exception as e:
                logger.critical(f"Scheduler error: {e}")

    async def stop(self) -> None:
        """Остановить scheduler."""
        self._running = False

    async def _check_all_links(self) -> None:
        """Проверить все ссылки."""

        page = 0

        while True:
            batch: PaginatedLink[GlobalLink] = (
                await self._service.get_all_links_paginated(page, self._batch_size)
            )

            if not batch.items:
                break

            links_to_notify = await self._get_links_for_notify(batch.items)

            if links_to_notify:
                logger.info(f"Find {len(links_to_notify)} links for update.")
                await self._send_update(links_to_notify)

            if not batch.has_next:
                break

            page += 1

    async def _send_update(self, link_events: list[LinkEvent]) -> None:
        """Подготовить Update."""
        updates: list[LinkUpdate] = []

        for link in link_events:
            chats = await self._service.get_chats_for_link(link.link_id)

            updates.append(
                LinkUpdate(
                    id=link.link_id,
                    description=str(link.event),
                    url=str(link.url),
                    tgChatIds=chats,
                )
            )

        if updates:
            await self._notifier.notify(updates)

    async def _get_links_for_notify(self, links: list[GlobalLink]) -> list[LinkEvent]:
        tasks = [self._check_single_link(link) for link in links]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [r for r in results if isinstance(r, LinkEvent)]

    async def _check_single_link(self, link: GlobalLink) -> Optional[LinkEvent]:
        async with self._sem:
            client = self._select_client(str(link.url))

            if not client:
                return None

            try:
                event = await client.get_last_event(str(link.url))
            except Exception as e:
                logger.warning("Client error", extra={"error": e, "url": str(link.url)})
                return None

            if not event:
                return None

            if self._needs_update(link, event.updated_at):
                await self._service.update_link_timestamp(link.id, event.updated_at)
                return LinkEvent(link_id=link.id, event=event, url=str(link.url))

            return None

    def _select_client(self, url: str) -> Optional[BaseClient]:
        for client in self._clients:
            if client.validate_url(url):
                return client
        return None

    def _needs_update(self, link: GlobalLink, new_date: datetime) -> bool:
        if link.updated_at is None:
            return True

        return new_date.replace(tzinfo=None) > link.updated_at.replace(tzinfo=None)
