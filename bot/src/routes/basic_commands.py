from constants.messages import BasicCommandMessage
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command, CommandStart
from metrics import command_duration, command_requests
import time
import logging

basic_commands = Router()
logger = logging.getLogger(__name__)


@basic_commands.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Обработчик команды /start."""
    command_requests.labels(command="start").inc()

    try:
        start = time.monotonic()
        await message.answer(BasicCommandMessage.START_ANSWER)
        logger.info(
            "The command /start was received.",
            extra={
                "user_id": message.from_user.id,
                "username": message.from_user.username,
            },
        )
        command_duration.labels(
            scope="bot_command", scope_type="start"
        ).observe((time.monotonic() - start) * 1000)
    except Exception as e:
        logger.error(
            "Error processing /start",
            extra={
                "user_id": message.from_user.id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )


@basic_commands.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Обработчик команды /help."""
    command_requests.labels(command="help").inc()
    try:
        start = time.monotonic()
        await message.answer(BasicCommandMessage.get_help_answer())

        logger.info(
            "The command /help was received.",
            extra={
                "user_id": message.from_user.id,
                "username": message.from_user.username,
            },
        )

        command_duration.labels(
            scope="bot_command", scope_type="help"
        ).observe((time.monotonic() - start) * 1000)
    except Exception as e:
        logger.error(
            "Error processing /help",
            extra={
                "user_id": message.from_user.id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )


@basic_commands.message()
async def handle_unknown_message(message: Message) -> None:
    """Обработчик неизвестной команды."""
    command_requests.labels(command="unknown").inc()

    try:
        start = time.monotonic()
        await message.answer(BasicCommandMessage.UNKNOWN_MESSAGES)

        logger.warning(
            "An unknown command was processed.",
            extra={
                "user_id": message.from_user.id,
                "username": message.from_user.username,
                "command": message.text,
            },
        )
        command_duration.labels(
            scope="bot_command", scope_type="unknown"
        ).observe((time.monotonic() - start) * 1000)
    except Exception as e:
        logger.error(
            "An unknown command was processed.",
            extra={
                "user_id": message.from_user.id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
