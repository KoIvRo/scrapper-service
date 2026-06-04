from models.dto import LinkUpdate
from filters.base_filter import BaseFilter
from summarizer import Summarizer
from models.dto import ProcessedUpdate
from prioritizer import Prioritizer
from grouper import Grouper
import logging

logger = logging.getLogger(__name__)


class Processor:
    """Класс для обработки обновления."""

    def __init__(
        self,
        filters: list[BaseFilter],
        summarizer: Summarizer,
        prioritizer: Prioritizer,
        grouper: Grouper,
    ) -> None:
        self._filters = filters
        self._summarizer = summarizer
        self._prioritizer = prioritizer
        self._grouper = grouper

    async def process_update(self, update: LinkUpdate) -> ProcessedUpdate:
        """Обработать обновление."""

        if not self._process_filters(update):
            return

        logger.info("Update wasnt filtered", extra={"url": str(update.url)})

        summary = await self._summarizer.summarize(update.description)

        logger.info("Text was summarized", extra={"url": str(update.url)})

        priority = self._prioritizer.prioritize(update.description)

        logger.info("Update was prioritized", extra={"url": str(update.url)})

        processed_update = ProcessedUpdate(
            priority=priority, description=summary, tgChatIds=update.tgChatIds
        )

        await self._grouper.add(processed_update)

    def _process_filters(self, update: LinkUpdate) -> bool:
        """Прогнать обновление по фильтрам."""

        for filt in self._filters:
            if filt.filter(update):
                logger.info("Update was discarded", extra={"url": str(update.url), "filter": {filt.__class__.__name__}})
                return False
        return True
