import asyncio
from pathlib import Path
from confluent_kafka import Consumer, KafkaError
from models.schemas import LinkUpdate
from .update_handler import handle_update
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import logging

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Консьюмер для kafka."""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        schema_registry_url: str,
    ):
        schema_registry_conf = {"url": schema_registry_url}
        self._schema_registry = SchemaRegistryClient(schema_registry_conf)
        self._create_schema_registry()

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

        logger.info("Kafka consumer started", extra={"topic": self._topic})

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
                update: LinkUpdate = self._avro_deserializer(
                    message.value(),
                    SerializationContext(self._topic, MessageField.VALUE),
                )

                if update.updated_id in self._processed_id:
                    logger.warning(
                        "Duplicate message detected",
                        extra={"url": str(update.url), "updated_id": update.updated_id},
                    )
                    await loop.run_in_executor(None, self._consumer.commit, message)
                    continue

                await handle_update(update)
                self._processed_id.add(update.updated_id)
                await loop.run_in_executor(None, self._consumer.commit, message)

                logger.info("Message was received", extra={"url": str(update.url)})

            except Exception as e:
                logger.error("Failed to process message", extra={"error": e})

    def stop(self):
        self._running = False
        self._consumer.close()

    def _create_schema_registry(self) -> None:
        schema_path = Path(__file__).parent.parent / "models" / "link.processed-updates.avsc"

        with open(schema_path, "r") as f:
            schema_str = f.read()

        self._avro_deserializer = AvroDeserializer(
            self._schema_registry,
            schema_str,
            lambda data, ctx: LinkUpdate(
                updated_id=data["updated_id"],
                id=data["id"],
                author=data["author"],
                url=data["url"],
                description=data["description"],
                tgChatIds=data["tgChatIds"],
            ),
        )
