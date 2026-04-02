from config import settings
from repository.base_repository import BaseRepository
from repository.raw_repository import RawRepository
from repository.orm_repository import OrmRepository


class RepositoryFactory:
    """Фабрика для рпеозитория."""

    def __init__(self) -> None:
        self._repository: BaseRepository = None

    def get_repository(self) -> BaseRepository:
        """Поулчения репозитория"""

        if not self._repository:
            self._repository = self.create_repository()

        return self._repository

    def create_repository(self) -> BaseRepository:
        """Создание репозитория."""

        host = settings.postgres_host
        port = settings.postgres_port
        user = settings.postgres_user
        db = settings.postgres_db
        password = settings.postgres_password.get_secret_value()

        if settings.access_type == "orm":
            self._repository = OrmRepository(
                host=host, port=port, user=user, db=db, password=password
            )
        else:
            self._repository = RawRepository(
                host=host, port=port, user=user, db=db, password=password
            )

        return self._repository


repository_factory = RepositoryFactory()


def get_repository() -> BaseRepository:
    """Получение репозитория."""
    return repository_factory.get_repository()
