from config import settings
from kafka.consumer import KafkaConsumer
from .processor_factory import get_processor
from typing import Optional


class ConsumerFactory:
    """Фабрика для Kafka."""

    def __init__(self) -> None:
        self._consumer: Optional[KafkaConsumer] = None

    def get_consumer(self) -> KafkaConsumer:
        """Получть consumer."""

        if self._consumer is None:
            self._consumer = KafkaConsumer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                topic=settings.kafka_consumer_topic,
                group_id=settings.kafka_consumer_group,
                schema_registry_url=settings.kafka_schema_registry_url,
                processor=get_processor(),
            )

        return self._consumer


consumer_factory = ConsumerFactory()


def get_consumer() -> KafkaConsumer:
    """Получить consumer."""

    return consumer_factory.get_consumer()
