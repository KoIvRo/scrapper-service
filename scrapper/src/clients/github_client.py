from httpx import Response
from typing import Optional
from datetime import datetime
from .base_client import BaseClient
from models.dto.schemas import GitHubEvent
from validators.validators import GitHubUrlValidator


class GitHubClient(BaseClient):
    """Клиент для гитхаба."""

    def __init__(self, token: str, validator: GitHubUrlValidator) -> None:
        super().__init__(base_url="https://api.github.com", validator=validator)
        self._token = token

    async def get_last_event(self, url: str) -> Optional[GitHubEvent]:
        """Получение времени последнего апдейта."""

        owner, repo = self._parse_url(url)
        client = await self._get_client()

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self._token}",
        }

        params: dict[str, str | int] = {
            "state": "all",
            "sort": "created",
            "direction": "desc",
            "per_page": 1,
        }

        response = await client.get(
            f"{self.base_url}/repos/{owner}/{repo}/issues",
            headers=headers,
            params=params,
        )

        if response.status_code == 200:
            update = self._parse_response(response)
            return update

        return None

    def _parse_response(self, response: Response) -> Optional[GitHubEvent]:
        """Получение даты обновления из ответа."""
        data: list = response.json()

        if not data:
            return None

        item: dict = data[0]

        updated_at = item.get("updated_at", None)
        if not updated_at:
            return None
        updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

        return GitHubEvent(
            url=item.get("html_url", ""),
            title=item.get("title", ""),
            author=item.get("user", {}).get("login", ""),
            updated_at=updated_at,
            preview=(item.get("body") or "")[:200],
        )

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
