from httpx import Response
from typing import Optional
from datetime import datetime
from .base_client import BaseClient
from validators.validators import GitHubUrlValidator


class GitHubClient(BaseClient):
    """Клиент для гитхаба."""

    def __init__(self, token: str, validator: GitHubUrlValidator) -> None:
        super().__init__(base_url="https://api.github.com", validator=validator)
        self._token = token

    async def get_last_update(self, url: str) -> Optional[datetime]:
        """Получение времени последнего апдейта."""

        owner, repo = self._parse_url(url)
        client = await self._get_client()

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self._token}",
        }

        response = await client.get(
            f"{self.base_url}/repos/{owner}/{repo}", headers=headers
        )

        if response.status_code == 200:
            updated_at = self._parse_response(response)

            if updated_at:
                return updated_at
        return None

    def _parse_response(self, response: Response) -> Optional[datetime]:
        """Получение даты обновления из ответа."""
        data: dict = response.json()
        updated_at: Optional[str] = data.get("updated_at", None)
        if updated_at:
            return datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return None

    def validate_url(self, url: str) -> bool:
        """Проверка подходящий ли url."""

        return self._validator.validate_url(url)

    def _parse_url(self, url: str) -> tuple[str, str]:
        """Парсинг url."""
        if self.validate_url(url):
            url_parts = url.split("/")
            return url_parts[-2], url_parts[-1]  # repos/{owner}/{repo}
        else:
            raise ValueError("Unknown URL")
