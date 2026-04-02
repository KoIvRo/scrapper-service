from config import settings
from routes.basic_commands import basic_commands
from routes.track import track
from routes.untrack import untrack
from routes.list import list_command
from routes.commands import setup_bot_commands
from aiogram import Bot, Dispatcher
from logger_config import setup_logger
from typing import Optional

logger = setup_logger(__name__)


class BotFactory:
    """Сиглтон бота."""

    def __init__(self) -> None:
        self._bot: Optional[Bot] = None
        self._dispathcer: Optional[Dispatcher] = None
        self._is_setup = False

    def get_bot(self) -> Bot:
        """Поулчить бота."""

        if not self._bot:
            self._bot = Bot(token=settings.bot_token.get_secret_value())
            logger.info(
                "Бот создан",
            )

        return self._bot

    def get_dispatcher(self) -> Dispatcher:
        """Получить диспатчер."""

        if not self._dispathcer:
            self._dispathcer = Dispatcher()
            self._dispathcer.include_routers(
                list_command, track, untrack, basic_commands
            )

        return self._dispathcer

    async def setup(self) -> None:
        """Настройка команд бота."""

        if not self._is_setup:
            await setup_bot_commands(self.get_bot())
            self._is_setup = True
            logger.info(
                "Команды установленны",
            )


bot_factory = BotFactory()


def get_bot() -> Bot:
    """Получить бота."""
    return bot_factory.get_bot()


def get_dispatcher() -> Dispatcher:
    """Получить диспатчер."""
    return bot_factory.get_dispatcher()
