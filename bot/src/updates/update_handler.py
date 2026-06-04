from models.schemas import ProcessedUpdate
from bot_instance import get_bot
import logging

logger = logging.getLogger(__name__)


async def handle_update(update: ProcessedUpdate) -> None:
    """Отправка сообщения в бота."""

    bot = get_bot()

    for chat_id in update.tgChatIds:
        await bot.send_message(chat_id=chat_id, text=f"Приоритет: {update.priority}\n{update.description}")

    logger.info("Update sent", extra={"count_chats": len(update.tgChatIds)})
