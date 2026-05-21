from config import settings
from models.dto import LinkUpdate
from .base_filter import BaseFilter


class AuthorFilter(BaseFilter):
    """Отфильтрока по автору."""

    @staticmethod
    def filter(update: LinkUpdate) -> bool:
        """Отфильтровать по автору."""
        return update.author in settings.filters.authors
