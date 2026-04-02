from unittest.mock import patch

from clients.base_client import BaseClient
from dependencies.service_factory import service_factory
from dependencies.repository_factory import (
    get_repository,
    repository_factory,
)


class TestRepositoryFactory:
    """Тест фабрики репозиториев."""

    def test_repository_singleton(self):
        """Репозиторий создается один раз."""

        repo1 = get_repository()
        repo2 = get_repository()

        assert repo1 is repo2

    def test_repository_factory_instance(self):
        """Фабрика кеширует репозиторий."""

        repo1 = repository_factory.get_repository()
        repo2 = repository_factory.get_repository()

        assert repo1 is repo2

    def test_repository_creation(self):
        """Репозиторий создается корректно."""

        repo = repository_factory.create_repository()

        assert repo is not None


class TestServiceFactory:
    """Тест фабрики сервисов."""

    def test_factory_singleton(self):
        """Фабрика создает один экземпляр сервиса."""

        service1 = service_factory.get_service()
        service2 = service_factory.get_service()

        assert service1 is service2


class TestClientFactory:
    """Тест фабрики клиентов."""

    def test_factory_singleton(self, client_factory):
        """Проверка синглтона."""
        with patch("src.dependencies.client_factory.settings") as mock_settings:
            mock_settings.github_token.get_secret_value.return_value = "test_token"

            github_client1 = client_factory.get_github_client()
            github_client2 = client_factory.get_github_client()

            assert client_factory._github_client is not None
            assert github_client1 is github_client2

    def test_factory_all(self, client_factory):
        """Проверка выдачи всех клиентов."""
        with patch("src.dependencies.client_factory.settings") as mock_settings:
            mock_settings.github_token.get_secret_value.return_value = "test_token"

            all_clients = client_factory.get_all_clients()

            assert len(all_clients) == 2
            assert all(
                client for client in all_clients if isinstance(client, BaseClient)
            )


class TestNotifierFactory:
    """Тест фабрики нотификатора."""

    def test_factory_singleton(self, notifier_factory):
        """Проверка синглтона."""
        not1 = notifier_factory.get_notifier()
        not2 = notifier_factory.get_notifier()

        assert notifier_factory._notifier is not None
        assert not1 is not2
