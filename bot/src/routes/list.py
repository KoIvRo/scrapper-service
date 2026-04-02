from aiogram import Router
from aiogram.fsm.context import FSMContext
from typing import Optional
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .states import ListStates
from logger_config import setup_logger
from constants.messages import TrackMessages
from dependencies.client_factory import get_client
from models.schemas import ListLinksResponse, LinkResponse
from constants.messages import ListMessages

logger = setup_logger(__name__)
list_command = Router()


def build_pagination_kb(
    page: int, has_next: bool, has_prev: bool
) -> InlineKeyboardMarkup:
    buttons = []

    if has_prev:
        buttons.append(InlineKeyboardButton(text="Назад", callback_data="prev"))

    if has_next:
        buttons.append(InlineKeyboardButton(text="Вперед", callback_data="next"))

    buttons.append(InlineKeyboardButton(text="Отмена", callback_data="cancel"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


@list_command.message(Command("list"))
async def track_list(message: Message, state: FSMContext) -> None:
    page = 0
    limit = 5
    tag = _extract_tag(message.text)

    client = get_client()

    response: ListLinksResponse = await client.get_links(message.chat.id, page, limit)
    links = _filter_links(response.links, tag)

    if not links:
        await message.answer(TrackMessages.LINKS_ARE_MISSING)
        return

    await state.set_data({"page": page, "limit": limit, "tag": tag})

    await state.set_state(ListStates.waiting_for_command)

    kb = build_pagination_kb(page, response.has_next, False)

    await message.answer(
        TrackMessages.get_links(links) if links else TrackMessages.LINKS_ARE_MISSING,
        reply_markup=kb,
    )


@list_command.callback_query(ListStates.waiting_for_command)
async def waiting_for_command(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    page = data["page"]
    limit = data["limit"]
    tag = data.get("tag")

    if callback.data == "cancel":
        await state.clear()
        await callback.answer(ListMessages.EXIT_LIST)
        return

    if callback.data == "next":
        page += 1

    elif callback.data == "prev":
        page = max(0, page - 1)

    client = get_client()

    response: ListLinksResponse = await client.get_links(
        callback.message.chat.id, page, limit
    )
    links = _filter_links(response.links, tag)

    await state.update_data(page=page)

    kb = build_pagination_kb(page, response.has_next, page > 0)

    await callback.message.edit_text(
        TrackMessages.get_links(links) if links else TrackMessages.LINKS_ARE_MISSING,
        reply_markup=kb,
    )

    await callback.answer()


@list_command.message(ListStates.waiting_for_command)
async def block_messages(message: Message) -> None:
    await message.answer(ListMessages.COMMAND_WARNING)


def _extract_tag(command: str) -> Optional[str]:
    parts = command.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else None


def _filter_links(links: list[LinkResponse], tag: Optional[str]) -> list[LinkResponse]:
    if tag:
        links = [link for link in links if tag in link.tags]
    return links
