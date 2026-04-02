import pytest
from unittest.mock import AsyncMock, patch
from models.schemas import ListLinksResponse, LinkResponse
from routes.list import track_list
from routes.list import _extract_tag


class TestListCommand:
    """Тесты для команды /list."""

    @pytest.mark.asyncio
    async def test_list_command_no_tag(self, message_factory, mock_bot):
        """Тест: /list без тега возвращает все ссылки."""

        message = message_factory("/list")

        mock_client = AsyncMock()
        mock_state = AsyncMock()

        mock_client.get_links.return_value = ListLinksResponse(
            links=[
                LinkResponse(
                    id=1, url="https://github.com/user/repo1", tags=["work"], filters=[]
                ),
                LinkResponse(
                    id=2,
                    url="https://github.com/user/repo2",
                    tags=["hobby"],
                    filters=[],
                ),
            ],
            size=2,
            has_next=True,
        )

        with patch("routes.list.get_client", return_value=mock_client):
            await track_list(message, mock_state)
            message.answer.assert_called_once()
            call_args = message.answer.call_args[0][0]
            assert "Ваши отслеживаемые ссылки" in call_args
            assert "repo1" in call_args
            assert "repo2" in call_args

    @pytest.mark.asyncio
    async def test_list_command_with_tag(self, message_factory, mock_bot):
        """Тест: /list work возвращает только ссылки с тегом work."""

        message = message_factory("/list work")

        mock_client = AsyncMock()
        mock_state = AsyncMock()
        mock_client.get_links.return_value = ListLinksResponse(
            links=[
                LinkResponse(
                    id=1, url="https://github.com/user/repo1", tags=["work"], filters=[]
                ),
                LinkResponse(
                    id=2,
                    url="https://github.com/user/repo2",
                    tags=["hobby"],
                    filters=[],
                ),
            ],
            size=2,
            has_next=True,
        )

        with patch("routes.list.get_client", return_value=mock_client):
            await track_list(message, mock_state)
            message.answer.assert_called_once()
            call_args = message.answer.call_args[0][0]
            assert "repo1" in call_args
            assert "repo2" not in call_args

    @pytest.mark.asyncio
    async def test_list_command_empty(self, message_factory, mock_bot):
        """Тест: /list когда нет ссылок."""

        message = message_factory("/list")

        mock_client = AsyncMock()
        mock_state = AsyncMock()
        mock_client.get_links.return_value = ListLinksResponse(
            links=[], size=0, has_next=False
        )

        with patch("routes.list.get_client", return_value=mock_client):
            await track_list(message, mock_state)
            message.answer.assert_called_once_with("У вас нет отслеживаемых ссылок")

    @pytest.mark.asyncio
    async def test_list_command_tag_no_matches(self, message_factory, mock_bot):
        """Тест: /list с тегом, который ничего не находит."""

        message = message_factory("/list python")

        mock_client = AsyncMock()
        mock_state = AsyncMock()
        mock_client.get_links.return_value = ListLinksResponse(
            links=[
                LinkResponse(
                    id=1, url="https://github.com/user/repo1", tags=["work"], filters=[]
                ),
            ],
            size=1,
            has_next=False,
        )

        with patch("routes.list.get_client", return_value=mock_client):
            await track_list(message, mock_state)

            message.answer.assert_called_once_with("У вас нет отслеживаемых ссылок")

    def test_extract_tag(self):
        """Тест извлечения тега из команды."""

        assert _extract_tag("/list") is None
        assert _extract_tag("/list work") == "work"
        assert _extract_tag("/list   python  ") == "python  "
