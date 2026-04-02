from aiogram import Bot
from typing import TypedDict
from aiogram.types import BotCommand


class Command(TypedDict):
    """Аннотация для команд."""

    command: str
    description: str


COMMANDS: list[Command] = [
    {"command": "start", "description": "Начните работу!"},
    {"command": "help", "description": "Воспользуйтесь помощью!"},
    {"command": "track", "description": "Начните отслеживать ссылку."},
    {"command": "untrack", "description": "Перестать отслеживать ссылку."},
    {"command": "list", "description": "Показать отслеживаемые ссылки."},
]


async def setup_bot_commands(bot: Bot) -> None:
    """Авторегистрация команд для бота."""

    commands = [
        BotCommand(command=cmd["command"], description=cmd["description"])
        for cmd in COMMANDS
    ]

    await bot.set_my_commands(commands)
