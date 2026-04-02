from config import settings
from typing import Optional
from notifier.bot_notifier import BotNotifier
from notifier.base_notifier import BaseNotifier


class NotifierFactory:
    """Фабрика для уведомителя."""

    def __init__(self) -> None:
        self._notifier: Optional[BaseNotifier] = None

    def get_notifier(self) -> BaseNotifier:
        """Получить уведомитель."""

        if self._notifier is None:
            self._notifier = BotNotifier(settings.bot_url)

        return self._notifier


notifier_factory = NotifierFactory()


def get_notifier() -> BaseNotifier:
    """Получить уведомитель."""

    return notifier_factory.get_notifier()
