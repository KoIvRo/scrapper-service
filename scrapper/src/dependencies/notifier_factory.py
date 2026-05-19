import httpx
from datetime import timedelta
from config import settings
from typing import Optional
from aiobreaker import CircuitBreaker
from notifier.http_notifier import HTTPNotifier
from notifier.kafka_notifier import KafkaNotifier
from notifier.base_notifier import BaseNotifier
import logging

logger = logging.getLogger(__name__)


class NotifierFactory:
    """Фабрика для уведомителя."""

    def __init__(self) -> None:
        self._kafka_notifier: Optional[KafkaNotifier] = None
        self._http_notifier: Optional[HTTPNotifier] = None

    def get_kafka_notifier(self) -> BaseNotifier:
        """Получить kafka уведомитель."""

        if self._kafka_notifier is None:
            self._kafka_notifier = self._create_kafka_notifier()

        return self._kafka_notifier

    def get_http_notifier(self) -> BaseNotifier:
        """Получть http уведомителя."""

        if self._http_notifier is None:
            self._http_notifier = self._create_http_notifier()

        return self._http_notifier

    def _create_kafka_notifier(self) -> KafkaNotifier:
        """Создать kafka уведомителя."""
        return KafkaNotifier(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            topic=settings.kafka_topic,
            schema_registry_url=settings.schema_registry_url,
        )

    def _create_http_notifier(self) -> BaseNotifier:
        """Создать уведомитель."""
        return HTTPNotifier(
            settings.bot_url,
            cb=CircuitBreaker(
                fail_max=settings.failure_threshold,
                timeout_duration=timedelta(seconds=settings.recovery_timeout),
                exclude=[httpx.HTTPError, httpx.RequestError],
            ),
        )


notifier_factory = NotifierFactory()


def get_kafka_notifier() -> KafkaNotifier:
    """Получить kafka уведомитель."""

    return notifier_factory.get_kafka_notifier()


def get_http_notifier() -> HTTPNotifier:
    """Получить http уведомителя."""

    return notifier_factory.get_http_notifier()
