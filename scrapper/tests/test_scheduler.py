from datetime import datetime
import pytest
from unittest.mock import AsyncMock, Mock

from scheduler import Scheduler
from models.dto.schemas import GlobalLink, PaginatedLink, LinkUpdate


class TestScheduler:
    """Тест планировщика."""

    @pytest.mark.asyncio
    async def test_get_links_for_notify_with_update(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        """Есть обновление (новая дата > старой)."""
        # Создаем ссылку со старой датой
        link = GlobalLink(
            id=1, url=sample_global_link.url, updated_at=datetime(2024, 1, 1, 10, 0, 0)
        )

        mock_service.get_all_links_paginated = AsyncMock(
            return_value=PaginatedLink(items=[link], has_next=False)
        )
        mock_client.get_last_update = AsyncMock(
            return_value=datetime(2024, 1, 2, 10, 0, 0)
        )
        mock_client.validate_url = Mock(return_value=True)

        scheduler = Scheduler(
            service=mock_service, clients=[mock_client], notifier=mock_notifier
        )

        # Вызываем внутренний метод
        result = await scheduler._get_links_for_notify([link])

        assert len(result) == 1
        assert result[0].updated_at == datetime(2024, 1, 2, 10, 0, 0)

    @pytest.mark.asyncio
    async def test_get_links_for_notify_client_not_valid(
        self, mock_service, mock_notifier, sample_global_link
    ):
        """Клиент не подходит для URL."""
        link = GlobalLink(id=1, url=sample_global_link.url, updated_at=None)

        mock_client = AsyncMock()
        mock_client.validate_url = Mock(return_value=False)
        mock_client.get_last_update = AsyncMock()

        scheduler = Scheduler(
            service=mock_service, clients=[mock_client], notifier=mock_notifier
        )

        result = await scheduler._get_links_for_notify([link])

        assert len(result) == 0
        mock_client.get_last_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_all_links_calls_notifier(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        """_check_all_links вызывает notifier если есть обновления."""
        # Создаем ссылку со старой датой
        link = GlobalLink(
            id=1, url=sample_global_link.url, updated_at=datetime(2024, 1, 1, 10, 0, 0)
        )

        # Настраиваем моки для пагинации
        mock_service.get_all_links_paginated = AsyncMock(
            return_value=PaginatedLink(items=[link], has_next=False)
        )
        mock_service.get_chats_for_link = AsyncMock(return_value=[123, 456])
        mock_service.update_link_timestamp = AsyncMock()

        mock_client.validate_url = Mock(return_value=True)
        mock_client.get_last_update = AsyncMock(
            return_value=datetime(2024, 1, 2, 10, 0, 0)
        )

        scheduler = Scheduler(
            service=mock_service, clients=[mock_client], notifier=mock_notifier
        )

        await scheduler._check_all_links()

        # Проверяем, что нотифаер был вызван
        mock_notifier.notify.assert_called_once()

        # Проверяем, что передан правильный LinkUpdate
        call_args = mock_notifier.notify.call_args[0][0]
        assert len(call_args) == 1
        assert isinstance(call_args[0], LinkUpdate)
        assert call_args[0].id == 1

    @pytest.mark.asyncio
    async def test_needs_update_when_no_previous_update(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        """Проверка обновления когда нет предыдущей даты."""
        link = GlobalLink(id=1, url=sample_global_link.url, updated_at=None)

        mock_client.validate_url = Mock(return_value=True)
        new_date = datetime(2024, 1, 2, 10, 0, 0)

        scheduler = Scheduler(
            service=mock_service, clients=[mock_client], notifier=mock_notifier
        )

        result = scheduler._needs_update(link, new_date)
        assert result is True

    @pytest.mark.asyncio
    async def test_needs_update_when_new_date_older(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        """Проверка обновления когда новая дата старше."""
        link = GlobalLink(
            id=1, url=sample_global_link.url, updated_at=datetime(2024, 1, 2, 10, 0, 0)
        )

        mock_client.validate_url = Mock(return_value=True)
        new_date = datetime(2024, 1, 1, 10, 0, 0)

        scheduler = Scheduler(
            service=mock_service, clients=[mock_client], notifier=mock_notifier
        )

        result = scheduler._needs_update(link, new_date)
        assert result is False

    @pytest.mark.asyncio
    async def test_select_client_found(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        """Выбор подходящего клиента."""
        mock_client.validate_url = Mock(return_value=True)

        scheduler = Scheduler(
            service=mock_service, clients=[mock_client], notifier=mock_notifier
        )

        result = scheduler._select_client("https://example.com")
        assert result == mock_client

    @pytest.mark.asyncio
    async def test_select_client_not_found(
        self, mock_service, mock_client, mock_notifier
    ):
        """Клиент не найден."""
        mock_client.validate_url = Mock(return_value=False)

        scheduler = Scheduler(
            service=mock_service, clients=[mock_client], notifier=mock_notifier
        )

        result = scheduler._select_client("https://example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_check_single_link_client_error(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        """Ошибка клиента при получении обновления."""
        link = GlobalLink(
            id=1, url=sample_global_link.url, updated_at=datetime(2024, 1, 1, 10, 0, 0)
        )

        mock_client.validate_url = Mock(return_value=True)
        mock_client.get_last_update = AsyncMock(side_effect=Exception("API Error"))

        scheduler = Scheduler(
            service=mock_service, clients=[mock_client], notifier=mock_notifier
        )

        result = await scheduler._check_single_link(link)
        assert result is None
        mock_service.update_link_timestamp.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_single_link_no_update(
        self, mock_service, mock_client, mock_notifier, sample_global_link
    ):
        """Нет обновления ссылки."""
        link = GlobalLink(
            id=1, url=sample_global_link.url, updated_at=datetime(2024, 1, 2, 10, 0, 0)
        )

        mock_client.validate_url = Mock(return_value=True)
        mock_client.get_last_update = AsyncMock(
            return_value=datetime(2024, 1, 2, 10, 0, 0)
        )

        scheduler = Scheduler(
            service=mock_service, clients=[mock_client], notifier=mock_notifier
        )

        result = await scheduler._check_single_link(link)
        assert result is None
        mock_service.update_link_timestamp.assert_not_called()
