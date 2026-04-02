import sys
import asyncio
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from config import settings
from api.updates import update
from logger_config import init_logger
from bot_instance import bot_factory, get_bot, get_dispatcher

sys.path.append(str(Path(__file__).parent))

app = FastAPI()
app.include_router(update)

async def run_api() -> None:
    """Запуск веб сервера."""
    config = uvicorn.Config(app, host=settings.host, port=settings.port)
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """Точка входа в приложение."""

    await bot_factory.setup()

    await asyncio.gather(get_dispatcher().start_polling(get_bot()), run_api())


if __name__ == "__main__":
    init_logger()
    asyncio.run(main())
