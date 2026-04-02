import pytest
from unittest.mock import AsyncMock, patch
from routes.untrack import start_untrack
from routes.untrack import waiting_for_links


class TestUntrackCommand:
    """Тесты для команды /untrack."""

    @pytest.mark.asyncio
    async def test_start_untrack(self, message_factory, mock_bot):
        message = message_factory("/untrack")
        mock_state = AsyncMock()

        await start_untrack(message, mock_state)

        message.answer.assert_called_once()
        mock_state.set_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_waiting_for_links_cancel(self, message_factory, mock_bot):
        message = message_factory("/cancel")
        mock_state = AsyncMock()

        await waiting_for_links(message, mock_state)

        mock_state.clear.assert_called_once()
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_waiting_for_links_delete_fail(self, message_factory, mock_bot):
        message = message_factory("https://github.com/user/repo")
        mock_state = AsyncMock()

        mock_client = AsyncMock()
        mock_client.delete_link.return_value = False

        with patch("routes.untrack.get_client", return_value=mock_client):
            await waiting_for_links(message, mock_state)

            message.answer.assert_called_once()
            mock_state.clear.assert_called_once()
