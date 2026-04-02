from models.dto.schemas import LinkUpdate
from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """Базовый класс уведомителя."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    async def notify(self, links: list[LinkUpdate]) -> None:
        pass
