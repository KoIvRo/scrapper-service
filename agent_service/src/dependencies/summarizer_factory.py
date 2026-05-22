import httpx
from summarizer import Summarizer
from config import settings
from typing import Optional


class SummarizerFacotry():
    """Фабрика для summarizer."""

    def __init__(self) -> None:
        self._summarizer: Optional[Summarizer] = None

    def get_summarizer(self) -> Summarizer:
        """Получить summarizer."""

        if self._summarizer is None:
            self._summarizer = Summarizer(
                threshold_words=settings.filters.threshold,
                timeout=httpx.Timeout(
                    connect=settings.timeout.connect,
                    read=settings.timeout.read,
                    write=settings.timeout.write,
                    pool=settings.timeout.pool
                )
            )
        
        return self._summarizer

summarizer_factory = SummarizerFacotry()

def get_summarizer() -> Summarizer:
    """Получить Summarizer."""

    return summarizer_factory.get_summarizer()
