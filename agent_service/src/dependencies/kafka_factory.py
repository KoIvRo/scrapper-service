from config import settings
from kafka.consumer import KafkaConsumer
from kafka.producer import KafkaNotifier
from typing import Optional


class KafkaFactory:
    """Фабрика для Kafka."""

    def __init__(self) -> None:
        self._producer: Optional[KafkaNotifier] = None
        self._consumer: Optional[KafkaConsumer] = None

    def get_consumer(self) -> KafkaConsumer:
        """Получть consumer."""

        if self._consumer is None:
            self._consumer = KafkaConsumer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                topic=settings.kafka_consumer_topic,
                group_id=settings.kafka_consumer_group,
                schema_registry_url=settings.kafka_schema_registry_url,
            )
        
        return self._consumer
    
    def get_producer(self) -> KafkaNotifier:
        """Получить producer."""

        if self._producer is None:
            self._producer = KafkaNotifier(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                topic=settings.kafka_producer_topic,
                schema_registry_url=settings.kafka_schema_registry_url,
            )
        
        return self._producer
    
kafka_factory = KafkaFactory()


def get_consumer() -> KafkaConsumer:
    """Получить consumer."""

    return kafka_factory.get_consumer()


def get_producer() -> KafkaNotifier:
    """Получить producer."""

    return kafka_factory.get_producer()
