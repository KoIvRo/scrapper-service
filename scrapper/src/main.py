import sys
import asyncio
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from api.links import links
from config import settings
from api.tg_chat import chats
from scheduler import Scheduler
from outbox_processor import OutboxProcessor
from dependencies.service_factory import get_service
from dependencies.notifier_factory import get_notifier
from dependencies.client_factory import get_clients_map
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from logger_config import init_logger


sys.path.append(str(Path(__file__).parent))

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(links)
app.include_router(chats)


async def run_api() -> None:
    """Запуск веб-сервера."""

    config = uvicorn.Config(app, host=settings.host, port=settings.port)
    server = uvicorn.Server(config)
    await server.serve()


async def run_scrapper() -> None:
    """Запуск сервиса."""

    service = get_service()
    clients_map = get_clients_map()
    notifier = get_notifier()

    if settings.notification_type == "kafka":
        scheduler = Scheduler(service, clients_map, notifier)
        outbox_processor = OutboxProcessor(service, notifier)
        await asyncio.gather(scheduler.start(), outbox_processor.start())
    else:
        scheduler = Scheduler(service, clients_map, notifier, use_outbox=False)
        await scheduler.start()


async def main() -> None:
    """Точка входа."""

    await asyncio.gather(run_api(), run_scrapper())


if __name__ == "__main__":
    init_logger()
    asyncio.run(main())
