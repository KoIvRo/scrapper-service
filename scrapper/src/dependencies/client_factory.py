from config import settings
from typing import Optional
from clients.base_client import BaseClient
from clients.github_client import GitHubClient
from clients.stackoverflow_client import StackOverFlowClient
from validators.validators import GitHubUrlValidator, StackOverFlowUrlValidator


class ClientFactory:
    """Фабрика клиентов."""

    def __init__(self) -> None:
        self._github_client: Optional[GitHubClient] = None
        self._stackoverflow_client: Optional[StackOverFlowClient] = None

    def get_github_client(self) -> GitHubClient:
        """Получение GitHub клиента."""

        if not self._github_client:
            self._github_client = GitHubClient(
                token=settings.github_token.get_secret_value(),
                validator=GitHubUrlValidator,
                timeout=settings.timeout
            )

        return self._github_client

    def get_stackoverflow_client(self) -> StackOverFlowClient:
        """Получение stackoverflow клиента."""

        if not self._stackoverflow_client:
            self._stackoverflow_client = StackOverFlowClient(
                validator=StackOverFlowUrlValidator,
                timeout=settings.timeout
            )

        return self._stackoverflow_client

    def get_all_clients(self) -> list[BaseClient]:
        """Получение всех клиентов списком."""

        return [self.get_github_client(), self.get_stackoverflow_client()]

    def get_clients_map(self) -> dict[str, BaseClient]:
        """Получение клиента за O(1)"""
        return {
            "github.com": self.get_github_client(),
            "stackoverflow.com": self.get_stackoverflow_client(),
        }


client_factory = ClientFactory()


def get_github_client() -> GitHubClient:
    """Получить гитхаб клиента из фабрики."""
    return client_factory.get_github_client()


def get_stackoverflow_client() -> StackOverFlowClient:
    """Получить stackoverflow клиента из фабрики."""
    return client_factory.get_stackoverflow_client()


def get_all_clients() -> list[BaseClient]:
    """Получение всех клиентов."""

    return client_factory.get_all_clients()


def get_clients_map() -> dict[str, BaseClient]:
    """Получение клиента за O(1)"""
    return client_factory.get_clients_map()
