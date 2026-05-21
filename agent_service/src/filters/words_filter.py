from config import settings
from models.dto import LinkUpdate
from .base_filter import BaseFilter


class WordsFilter(BaseFilter):
    """Фильтр по словам."""

    @staticmethod
    def filter(update: LinkUpdate) -> bool:
        """Фильтр по стоп словам."""
        text_lower = update.description.lower()
        words = text_lower.split()
        return any(word in words for word in settings.filters.stop_words)
