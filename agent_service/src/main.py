import asyncio
from config import settings
from kafka.consumer import KafkaConsumer
from logger_config import init_logger


async def run_consumer() -> None:
    """Запуск консьюмера."""

    consumer = KafkaConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        topic=settings.kafka_consumer_topic,
        group_id=settings.kafka_consumer_group,
        schema_registry_url=settings.kafka_schema_registry_url,
    )
    await consumer.start()


async def main() -> None:
    """Точка входа."""

    init_logger()

    await asyncio.gather(run_consumer())


if __name__ == "__main__":
    asyncio.run(main())
