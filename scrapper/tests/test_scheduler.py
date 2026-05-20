from datetime import datetime
import pytest
from unittest.mock import AsyncMock, Mock

from scheduler import Scheduler
from models.dto.schemas import GlobalLink, BaseEvent


class TestScheduler:
    def _mock_event(self, dt: datetime) -> BaseEvent:
        return BaseEvent(
            url="https://example.com",
            updated_at=dt,
            title="test",
            author="author",
            preview="preview",
        )

    @pytest.mark.asyncio
    async def test_get_links_for_notify_client_not_valid(
        self, mock_service, mock_notifier, sample_global_link
    ):
        link = GlobalLink(id=1, url=sample_global_link.url, updated_at=None)

        mock_client = AsyncMock()
        mock_client.validate_url = Mock(return_value=False)

        scheduler = Scheduler(
            service=mock_service,
            clients_map={"other.com": mock_client},
        )

        result = await scheduler._get_links_for_notify([link])

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_needs_update_when_no_previous_update(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        link = GlobalLink(id=1, url=sample_global_link.url, updated_at=None)

        scheduler = Scheduler(
            service=mock_service,
            clients_map={"example.com": mock_client},
        )

        result = scheduler._needs_update(link, datetime(2024, 1, 2, 10, 0, 0))
        assert result is True

    @pytest.mark.asyncio
    async def test_needs_update_when_new_date_older(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        link = GlobalLink(
            id=1,
            url=sample_global_link.url,
            updated_at=datetime(2024, 1, 2, 10, 0, 0),
        )

        scheduler = Scheduler(
            service=mock_service, clients_map={"example.com": mock_client}
        )

        result = scheduler._needs_update(link, datetime(2024, 1, 1, 10, 0, 0))
        assert result is False

    @pytest.mark.asyncio
    async def test_select_client_found(self, mock_service, mock_client, mock_notifier):
        mock_client.validate_url = Mock(return_value=True)

        scheduler = Scheduler(
            service=mock_service,
            clients_map={"example.com": mock_client},
        )

        result = scheduler._select_client("https://example.com")
        assert result == mock_client

    @pytest.mark.asyncio
    async def test_select_client_not_found(
        self, mock_service, mock_client, mock_notifier
    ):
        mock_client.validate_url = Mock(return_value=False)

        scheduler = Scheduler(
            service=mock_service,
            clients_map={"example.com": mock_client},
        )

        result = scheduler._select_client("https://other.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_check_single_link_client_error(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        link = GlobalLink(
            id=1,
            url=sample_global_link.url,
            updated_at=datetime(2024, 1, 1, 10, 0, 0),
        )

        mock_client.validate_url = Mock(return_value=True)
        mock_client.get_last_event = AsyncMock(side_effect=Exception("API Error"))

        scheduler = Scheduler(
            service=mock_service,
            clients_map={"example.com": mock_client},
        )

        result = await scheduler._check_single_link(link)

        assert result is None
        mock_service.update_link_timestamp.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_single_link_no_update(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        link = GlobalLink(
            id=1,
            url=sample_global_link.url,
            updated_at=datetime(2024, 1, 2, 10, 0, 0),
        )

        mock_client.validate_url = Mock(return_value=True)
        mock_client.get_last_event = AsyncMock(
            return_value=self._mock_event(datetime(2024, 1, 2, 10, 0, 0))
        )

        scheduler = Scheduler(
            service=mock_service,
            clients_map={"example.com": mock_client},
        )

        result = await scheduler._check_single_link(link)

        assert result is None
        mock_service.update_link_timestamp.assert_not_called()
