from validators.validators import VALIDATORS
from services.link_service import LinkService
from services.base_service import BaseService
from repository.base_repository import BaseRepository
from .repository_factory import get_repository


class ServiceFactory:
    """Файбрика зависимостей."""

    def __init__(self) -> None:
        self._link_service = None

    def get_service(self) -> BaseService:
        """Получение сервиса."""

        if self._link_service:
            return self._link_service

        repository: BaseRepository = get_repository()

        self._link_service = LinkService(repository, VALIDATORS)
        return self._link_service


service_factory = ServiceFactory()


def get_service() -> BaseService:
    """Получение сервиса."""
    return service_factory.get_service()
