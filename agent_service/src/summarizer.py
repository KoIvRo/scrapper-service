import httpx
from typing import Optional


class Summarizer:
    """Класс саммарайзер уведомлений."""

    def __init__(self, threshold_words: int, timeout: httpx.Timeout) -> None:
        self._client: Optional[httpx.AsyncClient] = None
        self._timeout = timeout
        self._threshold_words = threshold_words

    def _get_client(self) -> httpx.AsyncClient:
        """Получить клиента."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self._timeout)

    def summarize(self, description: str) -> str:
        """Сжатие текста (пока stub)."""
        # Добавить вызов API
        return f"{description[:self._threshold_words]}..."

    def is_need(self, len_description: int) -> bool:
        """Нужна ли саммаризация."""
        return len_description > self._threshold_words
