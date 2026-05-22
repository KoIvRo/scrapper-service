from models.dto import LinkUpdate
from filters.base_filter import BaseFilter
import logging

logger = logging.getLogger(__name__)


class Processor:
    """Класс для обработки обновления."""

    def __init__(self, filters: list[BaseFilter]) -> None:
        self._filters = filters

    async def process_update(self, update: LinkUpdate) -> None:
        """Обработать обновление."""
        
        if not await self._process_filters(update):
            return

    def _process_filters(self, update: LinkUpdate) -> bool:
        """Прогнать обновление по фильтрам."""

        for filt in self._filters:
            if filt.filter(update):
                logger.info("Update was discarded", extra={"name": str(update.url)})
                return False
        return True
