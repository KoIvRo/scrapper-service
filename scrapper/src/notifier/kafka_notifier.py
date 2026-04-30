import asyncio
from confluent_kafka import Producer
from .base_notifier import BaseNotifier
from models.dto.schemas import LinkUpdate
import logging

logger = logging.getLogger(__name__)


class KafkaNotifier(BaseNotifier):
    """Уведомление бота через Kafka."""

    def __init__(self, bootstrap_servers: str, topic: str) -> None:
        self._producer = Producer({"bootstrap.servers": bootstrap_servers,})
        self._topic = topic

    async def notify(self, links_updates: list[LinkUpdate]) -> None:
        """Отправка сообщений в Kafka."""
        loop = asyncio.get_event_loop()

        for update in links_updates:
            message = update.model_dump_json().encode("utf-8")

            await loop.run_in_executor(None, self._send_one(message))

        await loop.run_in_executor(None, self._producer.flush)

        logger.info("Send messages in Kafka", extra = {"count": len(links_updates), "topic": self._topic},)

    def _send_one(self, message: bytes) -> None:
        """Синхронная отправка одного сообщения."""
        self._producer.produce(self._topic, message)
