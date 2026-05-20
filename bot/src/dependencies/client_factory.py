import httpx
from config import settings
from client.base_client import BaseClient
from client.scrapper_client import ScrapperClient


class ClientFactory:
    """Фабрика синглтон для клиента."""

    def __init__(self):
        self._client = None

    def get_client(self) -> BaseClient:
        """Получение клиента."""
        if self._client is None:
            self._client = ScrapperClient(
                settings.service.scrapper_url,
                timeout=httpx.Timeout(
                    connect=settings.timeout.connect,
                    read=settings.timeout.read,
                    write=settings.timeout.write,
                    pool=settings.timeout.pool,
                ),
            )

        return self._client


client_factory = ClientFactory()


def get_client() -> BaseClient:
    """Получение клиента."""

    return client_factory.get_client()
