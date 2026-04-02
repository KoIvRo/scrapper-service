from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
from .states import TrackStates
from constants.messages import TrackMessages
from dependencies.client_factory import get_client
from pydantic import HttpUrl, ValidationError
import logging


track = Router()
logger = logging.getLogger(__name__)


@track.message(Command("track"))
async def start_track(message: Message, state=FSMContext) -> None:
    """Обработчик команды /track."""

    logger.info(
        "The /track command was received",
        extra={
            "user_id": message.from_user.id,
            "username": message.from_user.username,
        },
    )

    client = get_client()

    try:
        if await client.register_chat(message.chat.id):
            await message.answer(TrackMessages.START_TRACK)
            await state.set_state(TrackStates.waiting_for_links)
        else:
            await message.answer(TrackMessages.INVALID_CHAT)
            await state.clear()
    except Exception as e:
        await message.answer(f"{TrackMessages.ERROR}\n{e}")
        await state.clear()


@track.message(TrackStates.waiting_for_links)
async def waiting_for_links(message: Message, state=FSMContext) -> None:
    """Состояние ожидания ссылки."""

    logger.info(
        "Waiting link for append",
        extra={
            "user_id": message.from_user.id,
            "username": message.from_user.username,
        },
    )

    if message.text == "/cancel":
        await state.clear()
        await message.answer(TrackMessages.APPEND_CANCEL)
        return

    try:
        validate_url = HttpUrl(message.text)
        url = str(validate_url)
    except ValidationError:
        await message.answer(TrackMessages.INVALID_URL)
        return

    await state.update_data(link=url)

    await message.answer(TrackMessages.TAG_APPEND)
    await state.set_state(TrackStates.waiting_for_tags)


@track.message(TrackStates.waiting_for_tags)
async def waiting_for_tags(message: Message, state=FSMContext) -> None:
    """Состояние ожидания тегов."""

    logger.info(
        "Waiting for tags",
        extra={
            "user_id": message.from_user.id,
            "username": message.from_user.username,
        },
    )

    if message.text == "/cancel":
        await state.clear()
        await message.answer(TrackMessages.APPEND_CANCEL)
        return

    data = await state.get_data()
    url = data.get("link")

    if message.text == "/skip":
        await message.answer(TrackMessages.TAG_SKIP)
        tags = []
    else:
        tags = [tag.strip().lower() for tag in message.text.split(",") if tag.strip()]
        await message.answer(TrackMessages.get_tags_answer(tags))

    client = get_client()

    try:
        result = await client.append_link(chat_id=message.chat.id, url=url, tags=tags)

        if result:
            await message.answer(TrackMessages.get_url_answer(url))
            await state.clear()
        else:
            await message.answer(TrackMessages.INVALID_URL)
            await state.clear()
    except Exception:
        await message.answer(TrackMessages.ERROR)
        await state.clear()
