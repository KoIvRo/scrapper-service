from models.dto import LinkUpdate
from abc import ABC, abstractmethod



class BaseFilter(ABC):

    @abstractmethod
    def filter(update: LinkUpdate) -> bool:
        """Функция отфильтровки по параметру."""
        pass
