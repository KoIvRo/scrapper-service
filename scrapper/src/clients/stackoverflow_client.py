from typing import Optional, TypedDict
from datetime import datetime, timezone
from .base_client import BaseClient
from httpx import Response
from validators.validators import StackOverFlowUrlValidator
from models.dto.schemas import StackOverFlowEvent


class AnswersData(TypedDict):
    """Словарь с парсингом ответов."""

    author: str
    preview: str
    updated_at: datetime


class QuestionsData(TypedDict):
    """Словарь с парсингом вопроса."""

    url: str
    title: str


class StackOverFlowClient(BaseClient):
    """Клиент для stackoverflow."""

    def __init__(self, validator: StackOverFlowUrlValidator) -> None:
        super().__init__(base_url="https://api.stackexchange.com", validator=validator)

    async def get_last_event(self, url: str) -> Optional[StackOverFlowEvent]:
        """Получение последнего обновления."""

        client = await self._get_client()

        question_id = self._parse_url(url)

        params = {
            "site": "stackoverflow",
            "filter": "withbody",
            "sort": "activity",
            "order": "desc",
        }

        response_answers = await client.get(
            f"{self.base_url}/questions/{question_id}/answers",
            params=params,
        )

        response_questions = await client.get(
            f"{self.base_url}/questions/{question_id}",
            params=params,
        )

        if (
            response_answers.status_code == 200
            and response_questions.status_code == 200
        ):
            answers_data = self._parse_answers_response(response_answers)
            question_data = self._parse_questions_response(response_questions)
            return StackOverFlowEvent(
                title=question_data.get("title", ""),
                url=question_data.get("url", ""),
                author=answers_data.get("author", ""),
                preview=answers_data.get("preview", ""),
                updated_at=answers_data.get("updated_at", ""),
            )

        return None

    def _parse_answers_response(self, response_answers: Response) -> AnswersData:
        """Парсинг ответов."""
        data_answers: dict = response_answers.json()
        items_answers = data_answers.get("items", [])
        item_answers = items_answers[0]
        created_ts = item_answers.get("creation_date", None)
        created_at = datetime.fromtimestamp(created_ts, tz=timezone.utc)

        return {
            "author": item_answers.get("owner", {}).get("display_name", ""),
            "preview": (item_answers.get("body") or "")[:200],
            "updated_at": created_at,
        }

    def _parse_questions_response(self, response_questions: Response) -> QuestionsData:
        """Парсинг вопроса."""

        data_questions: dict = response_questions.json()
        item_questions = data_questions.get("items", [])[0]

        return {
            "url": item_questions.get("link", ""),
            "title": item_questions.get("title", ""),
        }

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
