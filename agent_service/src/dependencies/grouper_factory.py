from config import settings
from grouper import Grouper
from .producer_factory import get_producer
from typing import Optional


class GrouperFactory:
    """Фабрика для Grouper."""

    def __init__(self) -> None:
        self._grouper: Optional[Grouper] = None

    def get_grouper(self) -> Grouper:
        """Получить группровщик."""

        if self._grouper is None:
            self._grouper = Grouper(
                window_ms=settings.filters.window_ms, notifier=get_producer()
            )

        return self._grouper


grouper_factory = GrouperFactory()


def get_grouper() -> Grouper:
    """Получить группировщика."""
    return grouper_factory.get_grouper()
