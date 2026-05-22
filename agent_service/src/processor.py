from models.dto import LinkUpdate
from filters.base_filter import BaseFilter
from summarizer import Summarizer
import logging

logger = logging.getLogger(__name__)


class Processor:
    """Класс для обработки обновления."""

    def __init__(self, filters: list[BaseFilter], summarizer: Summarizer) -> None:
        self._filters = filters
        self._summarizer = summarizer

    async def process_update(self, update: LinkUpdate) -> None:
        """Обработать обновление."""

        if not await self._process_filters(update):
            return

        logger.info("Update wasnt filtered", extra={"url": str(update.url)})

        if self._summarizer.is_need(update.description):
            summary = self._summarizer.summarize(update.description)
            logger.info("Update was summarized", extra={"url": str(update.url)})

        # Передать в kafka
        processed_update = LinkUpdate(  # noqa
            id=update.id,
            author=update.author,
            url=str(update.url),
            description=summary,
            tgChatIds=update.tgChatIds,
        )

    def _process_filters(self, update: LinkUpdate) -> bool:
        """Прогнать обновление по фильтрам."""

        for filt in self._filters:
            if filt.filter(update):
                logger.info("Update was discarded", extra={"name": str(update.url)})
                return False
        return True
