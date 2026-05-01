from config import settings
from typing import Optional
from notifier.bot_notifier import BotNotifier
from notifier.kafka_notifier import KafkaNotifier
from notifier.base_notifier import BaseNotifier
import logging

logger = logging.getLogger(__name__)


class NotifierFactory:
    """Фабрика для уведомителя."""

    def __init__(self) -> None:
        self._notifier: Optional[BaseNotifier] = None

    def get_notifier(self) -> BaseNotifier:
        """Получить уведомитель."""

        if self._notifier is None:
            self._notifier = self._create_notifier()

        return self._notifier

    def _create_notifier(self) -> BaseNotifier:
        """Создать уведомитель."""
        if settings.notification_type == "kafka":
            logger.info(
                "Kafka producer creating",
                extra={
                    "topic": settings.kafka_topic,
                },
            )
            return KafkaNotifier(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                topic=settings.kafka_topic,
                schema_registry_url=settings.schema_registry_url,
            )
        else:
            logger.info("Bot notifier creating", extra={"bot_url": settings.bot_url})
            return BotNotifier(settings.bot_url)


notifier_factory = NotifierFactory()


def get_notifier() -> BaseNotifier:
    """Получить уведомитель."""

    return notifier_factory.get_notifier()
