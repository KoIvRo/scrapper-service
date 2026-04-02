from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from .states import UntrackStates
from constants.messages import UntrackMessages
from dependencies.client_factory import get_client
import logging

untrack = Router()
logger = logging.getLogger(__name__)


@untrack.message(Command("untrack"))
async def start_untrack(message: Message, state=FSMContext) -> None:
    """Обработчик команды /untrack."""

    logger.info(
        "The /track command was received.",
        extra={
            "user_id": message.from_user.id,
            "username": message.from_user.username,
        },
    )

    await message.answer(UntrackMessages.START_UNTRACK)
    await state.set_state(UntrackStates.waiting_for_links)


@untrack.message(UntrackStates.waiting_for_links)
async def waiting_for_links(message: Message, state=FSMContext) -> None:
    """Обработка состояния ожидания ссылки."""

    logger.info(
        "Waiting link for delete.",
        extra={
            "user_id": message.from_user.id,
            "username": message.from_user.username,
        },
    )

    if message.text == "/cancel":
        await state.clear()
        await message.answer(UntrackMessages.CANCEL_UNTRACK)
        return

    url = message.text
    client = get_client()
    try:
        response = await client.delete_link(message.chat.id, url)

        if response:
            await message.answer(UntrackMessages.get_untrack_answer(url))
            await state.clear()
        else:
            await message.answer(UntrackMessages.ERROR)
            await state.clear()
    except Exception:
        await message.answer(UntrackMessages.ERROR)
        await state.clear()
