import pytest
from unittest.mock import AsyncMock, patch, Mock


class TestGitHubClient:
    @pytest.mark.asyncio
    async def test_get_last_event_success(
        self,
        github_client,
        sample_github_url,
        mock_httpx_client,
    ):
        """Успешное получение события."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(
            return_value=[
                {
                    "html_url": "https://github.com/owner/repo/issues/1",
                    "title": "Test issue",
                    "user": {"login": "test_user"},
                    "updated_at": "2024-01-15T10:30:00Z",
                    "body": "Test body content",
                }
            ]
        )
        mock_httpx_client.get.return_value = mock_response

        with patch.object(github_client, "_get_client", return_value=mock_httpx_client):
            result = await github_client.get_last_event(sample_github_url)

        assert result is not None
        assert result.title == "Test issue"
        assert result.author == "test_user"
        assert result.url == "https://github.com/owner/repo/issues/1"
        assert result.preview.startswith("Test body")
        assert result.updated_at.year == 2024

    @pytest.mark.asyncio
    async def test_get_last_event_empty_response(
        self, github_client, sample_github_url, mock_httpx_client
    ):
        """Пустой список ответов."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value=[])
        mock_httpx_client.get.return_value = mock_response

        with patch.object(github_client, "_get_client", return_value=mock_httpx_client):
            result = await github_client.get_last_event(sample_github_url)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_last_event_no_updated_at(
        self, github_client, sample_github_url, mock_httpx_client
    ):
        """Нет updated_at."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(
            return_value=[
                {
                    "html_url": "https://github.com/owner/repo/issues/1",
                    "title": "Test issue",
                    "user": {"login": "test_user"},
                    "body": "Test body",
                }
            ]
        )
        mock_httpx_client.get.return_value = mock_response

        with patch.object(github_client, "_get_client", return_value=mock_httpx_client):
            result = await github_client.get_last_event(sample_github_url)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_last_event_not_found(
        self, github_client, sample_github_url, mock_httpx_client
    ):
        """404 от GitHub."""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_httpx_client.get.return_value = mock_response

        with patch.object(github_client, "_get_client", return_value=mock_httpx_client):
            result = await github_client.get_last_event(sample_github_url)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_last_event_api_error(
        self, github_client, sample_github_url, mock_httpx_client
    ):
        """Ошибка API."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_httpx_client.get.return_value = mock_response

        with patch.object(github_client, "_get_client", return_value=mock_httpx_client):
            result = await github_client.get_last_event(sample_github_url)

        assert result is None
