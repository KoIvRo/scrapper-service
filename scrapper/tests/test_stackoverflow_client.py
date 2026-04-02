import pytest
from datetime import datetime
from unittest.mock import Mock


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

    def test_parse_response_success(self, stackoverflow_client):
        """Тест успешного парсинга ответа."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [{"last_activity_date": 1705312800}]
        }

        result = stackoverflow_client._parse_response(mock_response)

        assert isinstance(result, datetime)
        assert result.year == 2024

    def test_parse_response_no_items(self, stackoverflow_client):
        """Тест парсинга ответа без элементов."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}

        result = stackoverflow_client._parse_response(mock_response)
        assert result is None

    def test_parse_response_no_date(self, stackoverflow_client):
        """Тест парсинга ответа без даты."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": [{"question_id": 123}]}

        result = stackoverflow_client._parse_response(mock_response)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_last_update_parse_error(self, stackoverflow_client):
        """Тест ошибки парсинга URL."""
        stackoverflow_client._parse_url = Mock(side_effect=ValueError("Unknown url"))

        with pytest.raises(ValueError, match="Unknown url"):
            await stackoverflow_client.get_last_update("https://invalid-url.com")
