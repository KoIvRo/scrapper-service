import sys
import asyncio
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from api.links import links
from config import settings
from api.tg_chat import chats
from scheduler import Scheduler
from dependencies.service_factory import get_service
from dependencies.notifier_factory import get_notifier
from dependencies.client_factory import get_all_clients


sys.path.append(str(Path(__file__).parent))

app = FastAPI()
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
    all_clients = get_all_clients()
    notifier = get_notifier()

    scheduler = Scheduler(service, all_clients, notifier)

    await scheduler.start()


async def main() -> None:
    """Точка входа."""

    await asyncio.gather(run_api(), run_scrapper())


if __name__ == "__main__":
    asyncio.run(main())
