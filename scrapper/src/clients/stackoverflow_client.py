from typing import Optional
from datetime import datetime, timezone
from .base_client import BaseClient
from httpx import Response
from validators.validators import StackOverFlowUrlValidator


class StackOverFlowClient(BaseClient):
    """Клиент для stackoverflow."""

    def __init__(self, validator: StackOverFlowUrlValidator) -> None:
        super().__init__(base_url="https://api.stackexchange.com", validator=validator)

    async def get_last_event(self, url: str) -> Optional[datetime]:
        """Получение последнего обновления."""

        client = await self._get_client()

        question_id = self._parse_url(url)

        response = await client.get(
            f"{self.base_url}/questions/{question_id}",
            params={"site": "stackoverflow", "filter": "withbody"},
        )

        if response.status_code == 200:
            updated_at = self._parse_response(response)
            if updated_at:
                return updated_at

        return None

    def _parse_response(self, response: Response) -> Optional[datetime]:
        """Получение даты обновления из ответа."""
        data: dict = response.json()
        items: Optional[dict] = data.get("items", None)
        if items:
            last_activity = items[0].get("last_activity_date")
            if last_activity:
                return datetime.fromtimestamp(last_activity, tz=timezone.utc)
        return None

    def _parse_url(self, url: str) -> int:
        if not self.validate_url(url):
            raise ValueError("Unknown url")

        url_parts = url.split("/")
        questions_index = url_parts.index("questions")

        question_id = int(url_parts[questions_index + 1])

        return question_id

    def validate_url(self, url: str) -> bool:
        """Валидация ссылки."""
        return self._validator.validate_url(url)
