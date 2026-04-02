import pytest
from unittest.mock import AsyncMock, patch, Mock
from datetime import datetime


class TestGitHubClient:
    @pytest.mark.asyncio
    async def test_get_last_update_success(
        self,
        github_client,
        sample_github_url,
        sample_github_response,
        mock_httpx_client,
    ):
        """Успешное обновление ссылки."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value=sample_github_response)
        mock_httpx_client.get.return_value = mock_response

        with patch.object(github_client, "_get_client", return_value=mock_httpx_client):
            result = await github_client.get_last_update(sample_github_url)

        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 2024

    @pytest.mark.asyncio
    async def test_get_last_update_not_found(
        self, github_client, sample_github_url, mock_httpx_client
    ):
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.json = Mock()
        mock_httpx_client.get.return_value = mock_response

        with patch.object(github_client, "_get_client", return_value=mock_httpx_client):
            result = await github_client.get_last_update(sample_github_url)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_last_update_api_error(
        self, github_client, sample_github_url, mock_httpx_client
    ):
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.json = Mock()
        mock_httpx_client.get.return_value = mock_response

        with patch.object(github_client, "_get_client", return_value=mock_httpx_client):
            result = await github_client.get_last_update(sample_github_url)

        assert result is None
