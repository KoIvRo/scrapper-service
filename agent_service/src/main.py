import asyncio
from config import settings
from dependencies.kafka_factory import get_consumer
from logger_config import init_logger


async def run_consumer() -> None:
    """Запуск консьюмера."""

    consumer = get_consumer()
    await consumer.start()


async def main() -> None:
    """Точка входа."""

    init_logger()

    await asyncio.gather(run_consumer())


if __name__ == "__main__":
    asyncio.run(main())
