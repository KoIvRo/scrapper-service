import asyncio
from pathlib import Path
from confluent_kafka import Producer
from models.dto import LinkUpdate
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
import logging

logger = logging.getLogger(__name__)


class KafkaNotifier:
    """Уведомление бота через Kafka."""

    def __init__(
        self, bootstrap_servers: str, topic: str, schema_registry_url: str
    ) -> None:
        self._topic = topic

        schema_registry_conf = {"url": schema_registry_url}
        self._schema_registry = SchemaRegistryClient(schema_registry_conf)

        self._producer = Producer(
            {
                "bootstrap.servers": bootstrap_servers,
            }
        )

        self._create_schema_registry()

    async def notify(self, links_updates: list[LinkUpdate]) -> None:
        """Отправка сообщений в Kafka."""
        loop = asyncio.get_event_loop()

        for update in links_updates:
            message = self._avro_serializer(
                update,
                SerializationContext(self._topic, MessageField.VALUE),
            )

            await loop.run_in_executor(None, self._send_one, message)

        await loop.run_in_executor(None, self._producer.flush)

        logger.info(
            "Send messages in Kafka",
            extra={"count": len(links_updates), "topic": self._topic},
        )

    def _create_schema_registry(self) -> None:
        schema_path = Path(__file__).parent.parent / "models" / "link.processed_update.avsc"

        with open(schema_path, "r") as f:
            schema_str = f.read()

        self._avro_serializer = AvroSerializer(
            self._schema_registry,
            schema_str,
            lambda update, ctx: {
                "updated_id": update.updated_id,
                "id": update.id,
                "url": str(update.url),
                "description": update.description,
                "tgChatIds": update.tgChatIds,
            },
        )

    def _send_one(self, message: bytes) -> None:
        """Синхронная отправка одного сообщения."""
        self._producer.produce(self._topic, message)
