from models.dto import Priority


class Prioritizer:
    """Класс для приоритезации сообщений."""

    def __init__(self, low_words: list[str], high_words: list[str]) -> None:
        self._low_words = low_words
        self._high_words = high_words

    def prioritize(self, description: str) -> str:
        text_lower = description.lower()

        for word in self._high_words:
            if word.lower() in text_lower:
                return Priority.HIGH.value

        for word in self._low_words:
            if word.lower() in text_lower:
                return Priority.LOW.value

        return Priority.MEDIUM.value
