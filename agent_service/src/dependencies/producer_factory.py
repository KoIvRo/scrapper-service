from config import settings
from kafka.consumer import KafkaConsumer
from kafka.producer import KafkaNotifier
from typing import Optional


class ProducerFactory:
    """Фабрика для Kafka."""

    def __init__(self) -> None:
        self._producer: Optional[KafkaNotifier] = None
    
    def get_producer(self) -> KafkaNotifier:
        """Получить producer."""

        if self._producer is None:
            self._producer = KafkaNotifier(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                topic=settings.kafka_producer_topic,
                schema_registry_url=settings.kafka_schema_registry_url,
            )
        
        return self._producer
    
kafka_factory = ProducerFactory()


def get_producer() -> KafkaNotifier:
    """Получить producer."""

    return kafka_factory.get_producer()
