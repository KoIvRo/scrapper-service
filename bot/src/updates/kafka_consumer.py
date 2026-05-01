import json
import asyncio
from confluent_kafka import Consumer, KafkaError
from models.schemas import LinkUpdate
from .update_handler import handle_update
import logging

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Консьюмер для kafka."""

    def __init__(self, bootstrap_servers: str, topic: str, group_id: str):
        self._consumer = Consumer(
            {
                "bootstrap.servers": bootstrap_servers,
                "group.id": group_id,
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )
        self._topic = topic
        self._running = False
        self._update_time = 1
        self._processed_id: set[str] = set()

    async def start(self):
        """Запуск чтения. handler — функция для обработки LinkUpdate."""
        self._consumer.subscribe([self._topic])
        self._running = True
        loop = asyncio.get_event_loop()

        logger.info(f"Kafka consumer started", extra={"topic": self._topic})

        while self._running:
            message = await loop.run_in_executor(
                None, self._consumer.poll, self._update_time
            )

            if message is None:
                continue

            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error("Consumer error", extra={"error": message.error()})
                continue

            try:
                data = json.loads(message.value().decode("utf-8"))
                update = LinkUpdate(**data)

                if update.updated_id in self._processed_id:
                    logger.warning("Duplicate message detected", extra={"url": str(update.url), "updated_id": update.updated_id})
                    await loop.run_in_executor(None, self._consumer.commit, message)
                    continue

                await handle_update(update)
                self._processed_id.add(update.updated_id)
                await loop.run_in_executor(None, self._consumer.commit, message)

                logger.info("Message was received", extra={"url": str(update.url)})

            except Exception as e:
                logger.error(f"Failed to process message", extra={"error": e})

    def stop(self):
        self._running = False
        self._consumer.close()
