import pytest
from unittest.mock import AsyncMock, patch
from routes.track import start_track
from routes.track import waiting_for_links
from routes.track import waiting_for_tags


class TestTrackCommand:
    """Тесты для команды /track."""

    @pytest.mark.asyncio
    async def test_start_track_register_fail(self, message_factory, mock_bot):
        message = message_factory("/track")
        mock_state = AsyncMock()
        mock_client = AsyncMock()
        mock_client.register_chat.return_value = False

        with patch("routes.track.get_client", return_value=mock_client):
            await start_track(message, mock_state)

            message.answer.assert_called_once()
            mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_waiting_for_links_valid(self, message_factory, mock_bot):
        message = message_factory("https://github.com/user/repo")
        mock_state = AsyncMock()

        await waiting_for_links(message, mock_state)

        mock_state.update_data.assert_called_once_with(
            link="https://github.com/user/repo"
        )
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
    async def test_waiting_for_tags_cancel(self, message_factory, mock_bot):
        message = message_factory("/cancel")
        mock_state = AsyncMock()

        await waiting_for_tags(message, mock_state)

        mock_state.clear.assert_called_once()
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_waiting_for_tags_append_fail(self, message_factory, mock_bot):
        message = message_factory("work")
        mock_state = AsyncMock()
        mock_state.get_data.return_value = {"link": "https://github.com/user/repo"}

        mock_client = AsyncMock()
        mock_client.append_link.return_value = None

        with patch("routes.track.get_client", return_value=mock_client):
            await waiting_for_tags(message, mock_state)

            message.answer.assert_called()
            mock_state.clear.assert_called_once()
