from typing import Optional
from httpx import AsyncClient
from models.schemas import ListLinksResponse


class ScrapperClient:
    """Клиент для scrapper-service."""

    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self.base_url = base_url
        self._client: Optional[AsyncClient] = None
        self._timeout = timeout

    async def get_links(self, chat_id: int, page: int, limit: int) -> ListLinksResponse:
        """Получение всех ссылок отселживаемых пользователем."""

        client = await self._get_client()

        try:
            response = await client.get(
                f"{self.base_url}/links/",
                params={"page": page, "limit": limit},
                headers={"Tg-Chat-Id": str(chat_id)},
            )

            if response.status_code == 200:
                return ListLinksResponse(**response.json())
            else:
                return ListLinksResponse(links=[], size=0, has_next=False)
        except Exception:
            return ListLinksResponse(links=[], size=0)

    async def register_chat(self, chat_id: int) -> bool:
        """Регистрация чата."""

        client = await self._get_client()

        try:
            response = await client.post(f"{self.base_url}/tg-chat/{chat_id}")

            if response.status_code == 200:
                return True
            elif response.status_code == 409:
                return True
            return False
        except Exception:
            return False

    async def delete_chat(self, chat_id: int) -> bool:
        """Удаление чата."""

        client = await self._get_client()

        try:
            response = await client.delete(f"{self.base_url}/tg-chat" / {chat_id})

            if response.status_code == 200:
                return True
            return False
        except Exception:
            return False

    async def append_link(self, chat_id: int, url: str, tags: Optional[str]) -> bool:
        """Добавление ссылки."""

        client = await self._get_client()

        payload = {"link": url, "tags": tags or [], "filters": []}  # пока не используем

        try:
            response = await client.post(
                f"{self.base_url}/links",
                headers={"Tg-Chat-Id": str(chat_id)},
                json=payload,
            )
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception:
            return False

    async def delete_link(self, chat_id: int, url: str) -> bool:
        """Удаление ссылки."""

        client = await self._get_client()

        payload = {"link": url}

        try:
            response = await client.request(
                method="DELETE",
                url=f"{self.base_url}/links",
                headers={"Tg-Chat-Id": str(chat_id)},
                json=payload,
            )
            if response.status_code == 200:
                return True
            return False
        except Exception:
            return False

    async def _get_client(self) -> AsyncClient:
        """Получить клиента."""

        if not self._client:
            self._client = AsyncClient(timeout=self._timeout)

        return self._client
