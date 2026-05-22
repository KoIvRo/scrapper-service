import httpx
from aiobreaker import CircuitBreaker
from summarizer import Summarizer
from datetime import timedelta
from config import settings
from typing import Optional


class SummarizerFactory:
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
                    pool=settings.timeout.pool,
                ),
                use_ai=settings.ai.use_ai,
                url=settings.ai.url,
                model=settings.ai.model,
                token=settings.ai_token,
                cb=CircuitBreaker(
                    fail_max=settings.circuit_breaker.failure_threshold,
                    timeout_duration=timedelta(
                        seconds=settings.circuit_breaker.recovery_timeout
                    ),
                    exclude=[httpx.HTTPError, httpx.RequestError],
                ),
            )

        return self._summarizer


summarizer_factory = SummarizerFactory()


def get_summarizer() -> Summarizer:
    """Получить Summarizer."""

    return summarizer_factory.get_summarizer()
