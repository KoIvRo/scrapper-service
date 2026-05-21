from filters.base_filter import BaseFilter


class Processor:
    """Класс для обработки обновления."""

    def __init__(self, filters: list[BaseFilter]) -> None:
        self._filters = filters

