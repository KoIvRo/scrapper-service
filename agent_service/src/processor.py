class Processor:
    """Класс для обработки обновления."""

    def __init__(self, filters: list, ai) -> None:
        self._filters = filters
        self._ai = ai
