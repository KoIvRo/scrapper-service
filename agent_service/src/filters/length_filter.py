from config import settings
from models.dto import LinkUpdate
from .base_filter import BaseFilter


class LengthFilter(BaseFilter):
    """Класс для фильтрации сообщения по длине."""

    @staticmethod
    def filter(update: LinkUpdate) -> bool:
        """Фильтрация по длине."""
        return len(update.description) < settings.filters.min_length
