from config import settings
from prioritizer import Prioritizer


class PrioritizerFactory:
    """Фабрика приоритезатора."""

    def __init__(self) -> None:
        self._prioritizer = None

    def get_prioritizer(self) -> Prioritizer:
        """Получение Prioritizer."""

        if self._prioritizer is None:
            self._prioritizer = Prioritizer(
                low_words=settings.filters.low_words,
                high_words=settings.filters.high_words,
            )

        return self._prioritizer


prioritizer_factory = PrioritizerFactory()


def get_prioritizer() -> Prioritizer:
    """Получить приоритезатор."""

    return prioritizer_factory.get_prioritizer()
