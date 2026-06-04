import asyncio
from collections import defaultdict
from models.dto import ProcessedUpdate, Priority
from kafka.producer import KafkaNotifier
import logging

logger = logging.getLogger(__name__)


class Grouper:
    """Группирует обновления по tgChatId в рамках временного окна."""

    def __init__(self, window_ms: int, notifier: KafkaNotifier):
        self._window_sec = window_ms / 1000
        self._buckets: dict[int, list[ProcessedUpdate]] = defaultdict(list)
        self._timers: dict[int, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._notifier = notifier

    async def add(self, update: ProcessedUpdate):
        """Добавить обновление в группу."""
        async with self._lock:
            for chat_id in update.tgChatIds:
                self._buckets[chat_id].append(update)

                if chat_id not in self._timers or self._timers[chat_id].done():
                    self._timers[chat_id] = asyncio.create_task(
                        self._flush_after_window(chat_id)
                    )

    async def _flush_after_window(self, chat_id: int):
        """Ждём окно и отправляем."""
        await asyncio.sleep(self._window_sec)

        async with self._lock:
            updates = self._buckets.pop(chat_id, [])
            self._timers.pop(chat_id, None)

        if not updates:
            return

        await self._flush(chat_id, updates)

    async def _flush(self, chat_id: int, updates: list[ProcessedUpdate]):
        """Сгруппировать и отправить."""
        if not updates:
            return

        if len(updates) == 1:
            processed = updates[0]
        else:
            descriptions = [
                f"{i+1}. {upd.description}" for i, upd in enumerate(updates)
            ]
            combined = "\n".join(descriptions)
            max_priority = self._max_priority(update.priority for update in updates)

            processed = ProcessedUpdate(
                priority=max_priority,
                description=combined,
                tgChatIds=[chat_id],
            )

        await self._notifier.notify(processed)
        logger.info(f"Flushed {len(updates)} updates for chat {chat_id}")

    def _max_priority(self, priorities: list[str]) -> str:
        order = {
            Priority.HIGH.value: 3,
            Priority.MEDIUM.value: 2,
            Priority.LOW.value: 1,
        }
        return max(priorities, key=lambda p: order[p])
