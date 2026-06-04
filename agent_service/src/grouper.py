import asyncio
from kafka.producer import KafkaNotifier
from models.dto import ProcessedUpdate


class Grouper:
    """Класс группировщик."""

    def __init__(self, window_ms: int, notifier: KafkaNotifier) -> None:
        self._window_ms = window_ms
        self._notifier = notifier

    