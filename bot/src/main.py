import sys
import asyncio
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from config import settings
from updates.api import update
from logger_config import init_logger
from bot_instance import bot_factory, get_bot, get_dispatcher
from updates.kafka_consumer import KafkaConsumer

sys.path.append(str(Path(__file__).parent))


async def run_api() -> None:
    """Запуск веб сервера."""
    app = FastAPI()
    app.include_router(update)
    config = uvicorn.Config(app, host=settings.host, port=settings.port)
    server = uvicorn.Server(config)
    await server.serve()


async def run_consumer() -> None:
    """Запуск консьюмера."""

    consumer = KafkaConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        topic=settings.kafka_topic,
        group_id=settings.kafka_consumer_group,
    )
    await consumer.start()


async def main() -> None:
    """Точка входа в приложение."""

    await bot_factory.setup()

    if settings.notification_type == "kafka":
        await asyncio.gather(get_dispatcher().start_polling(get_bot()), run_consumer())
    else:
        await asyncio.gather(get_dispatcher().start_polling(get_bot()), run_api())


if __name__ == "__main__":
    init_logger()
    asyncio.run(main())
