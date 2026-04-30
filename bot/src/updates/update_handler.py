from models.schemas import LinkUpdate
from bot_instance import get_bot
import logging

logger = logging.getLogger(__name__)


async def handle_update(update: LinkUpdate) -> None:
    """Отправка сообщения в бота."""

    bot = get_bot()

    for chat_id in update.tgChatIds:
        await bot.send_message(chat_id=chat_id, text=update.description)

    logger.info("Update sent", extra={"count_chats": len(update.tgChatIds)})
