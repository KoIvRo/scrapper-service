from validators.validators import VALIDATORS
from services.link_service import LinkService
from services.base_service import BaseService
from .repository_factory import get_repository
from .cache_factory import get_cache_manager


class ServiceFactory:
    """Файбрика зависимостей."""

    def __init__(self) -> None:
        self._link_service = None

    def get_service(self) -> BaseService:
        """Получение сервиса."""

        if self._link_service:
            return self._link_service

        repository = get_repository()
        cache_manager = get_cache_manager()

        self._link_service = LinkService(repository, cache_manager, VALIDATORS)
        return self._link_service


service_factory = ServiceFactory()


def get_service() -> BaseService:
    """Получение сервиса."""
    return service_factory.get_service()
