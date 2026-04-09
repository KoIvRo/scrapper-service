import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime


class TestStackOverFlowClient:
    """Тесты для StackOverflow клиента."""

    def test_parse_url_valid(self, stackoverflow_client):
        """Тест парсинга корректного URL."""
        stackoverflow_client._validator.validate_url.return_value = True

        test_cases = [
            ("https://stackoverflow.com/questions/123/", 123),
            ("https://stackoverflow.com/questions/456/test-question", 456),
            ("https://stackoverflow.com/questions/789", 789),
        ]

        for url, expected_id in test_cases:
            question_id = stackoverflow_client._parse_url(url)
            assert question_id == expected_id

    def test_parse_url_invalid(self, stackoverflow_client):
        """Тест парсинга некорректного URL."""
        stackoverflow_client._validator.validate_url.return_value = False

        with pytest.raises(ValueError, match="Unknown url"):
            stackoverflow_client._parse_url("https://google.com")

    def test_parse_answers_response_success(self, stackoverflow_client):
        """Успешный парсинг ответа."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "creation_date": 1705312800,
                    "owner": {"display_name": "user1"},
                    "body": "Test answer body",
                }
            ]
        }

        result = stackoverflow_client._parse_answers_response(mock_response)

        assert result is not None
        assert result["author"] == "user1"
        assert result["preview"].startswith("Test answer")
        assert isinstance(result["updated_at"], datetime)

    def test_parse_questions_response_success(self, stackoverflow_client):
        """Парсинг вопроса."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "link": "https://stackoverflow.com/questions/123",
                    "title": "Test question",
                }
            ]
        }

        result = stackoverflow_client._parse_questions_response(mock_response)

        assert result["url"] == "https://stackoverflow.com/questions/123"
        assert result["title"] == "Test question"

    @pytest.mark.asyncio
    async def test_get_last_event_success(
        self, stackoverflow_client, mock_httpx_client
    ):
        """Успешное получение события."""

        answers_response = AsyncMock()
        answers_response.status_code = 200
        answers_response.json = Mock(
            return_value={
                "items": [
                    {
                        "creation_date": 1705312800,
                        "owner": {"display_name": "user1"},
                        "body": "Answer body",
                    }
                ]
            }
        )

        questions_response = AsyncMock()
        questions_response.status_code = 200
        questions_response.json = Mock(
            return_value={
                "items": [
                    {
                        "link": "https://stackoverflow.com/questions/123",
                        "title": "Test question",
                    }
                ]
            }
        )

        mock_httpx_client.get.side_effect = [
            answers_response,
            questions_response,
        ]

        with patch.object(
            stackoverflow_client, "_get_client", return_value=mock_httpx_client
        ):
            with patch.object(stackoverflow_client, "_parse_url", return_value=123):
                result = await stackoverflow_client.get_last_event(
                    "https://stackoverflow.com/questions/123"
                )

        assert result is not None
        assert result.title == "Test question"
        assert result.author == "user1"
        assert result.preview.startswith("Answer body")

    @pytest.mark.asyncio
    async def test_get_last_event_parse_error(self, stackoverflow_client):
        """Ошибка парсинга URL."""
        stackoverflow_client._parse_url = Mock(side_effect=ValueError("Unknown url"))

        with pytest.raises(ValueError, match="Unknown url"):
            await stackoverflow_client.get_last_event("https://invalid-url.com")
