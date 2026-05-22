import pytest
from unittest.mock import AsyncMock, patch

from notifier.http_notifier import HTTPNotifier
from models.dto.schemas import LinkUpdate


class TestNotifier:
    """Тест HTTP-нотифаера."""

    @pytest.mark.asyncio
    async def test_create_update(self, sample_link):
        """Тест создания модели обновления."""
        update = LinkUpdate(
            id=sample_link.id,
            author="test-user",
            url=str(sample_link.url),
            description="Обнаружено изменение",
            tgChatIds=[sample_link.chat_id],
        )

        assert isinstance(update, LinkUpdate)
        assert update.id == sample_link.id
        assert update.url == str(sample_link.url)
        assert update.tgChatIds == [sample_link.chat_id]

    @pytest.mark.asyncio
    async def test_send_request_success(self, sample_link, mock_circuit_breaker):
        """Тест успешной отправки запроса."""
        notifier = HTTPNotifier("http://bot:8000", mock_circuit_breaker)

        mock_response = AsyncMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(notifier, "_get_client", return_value=mock_client):
            update = LinkUpdate(
                id=sample_link.id,
                url=str(sample_link.url),
                author="test-user",
                description="Обнаружено изменение",
                tgChatIds=[sample_link.chat_id],
            )

            await notifier._send_request(update)

            mock_client.post.assert_called_once()
            args, kwargs = mock_client.post.call_args

            assert args[0] == "http://bot:8000/updates"
            assert kwargs["json"]["id"] == sample_link.id
            assert kwargs["json"]["url"] == str(sample_link.url)

    @pytest.mark.asyncio
    async def test_notify_multiple_links(
        self, sample_link, another_link, mock_circuit_breaker
    ):
        """Тест отправки нескольких уведомлений."""
        notifier = HTTPNotifier("http://bot:8000", mock_circuit_breaker)

        with patch.object(notifier, "_send_request", new=AsyncMock()) as mock_send:
            await notifier.notify(
                [
                    LinkUpdate(
                        id=sample_link.id,
                        url=str(sample_link.url),
                        description="Обнаружено изменение",
                        author="test-user",
                        tgChatIds=[sample_link.chat_id],
                    ),
                    LinkUpdate(
                        id=another_link.id,
                        url=str(another_link.url),
                        description="Обнаружено изменение",
                        author="test-user",
                        tgChatIds=[another_link.chat_id],
                    ),
                ]
            )

            assert mock_send.call_count == 2

    @pytest.mark.asyncio
    async def test_notify_empty_list(self, mock_circuit_breaker):
        """Тест отправки пустого списка."""
        notifier = HTTPNotifier("http://bot:8000", mock_circuit_breaker)

        with patch.object(notifier, "_send_request", new=AsyncMock()) as mock_send:
            await notifier.notify([])

            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_client_lazy_initialization(self, mock_circuit_breaker):
        """Тест ленивой инициализации клиента."""
        notifier = HTTPNotifier("http://bot:8000", mock_circuit_breaker)

        assert notifier._client is None

        client = await notifier._get_client()
        assert client is not None

        client2 = await notifier._get_client()
        assert client is client2

    @pytest.mark.asyncio
    async def test_strftime_formatting(self, sample_link):
        """Тест форматирования даты."""
        update = LinkUpdate(
            id=sample_link.id,
            url=str(sample_link.url),
            author="test-user",
            description="Обнаружено изменение",
            tgChatIds=[sample_link.chat_id],
        )

        assert update.description == "Обнаружено изменение"
        assert "+00:00" not in update.description

    @pytest.mark.asyncio
    async def test_notify_http_fails_still_completes(
        self, sample_link, mock_circuit_breaker
    ):
        """
        TC-5.1: При ошибке HTTP не теряем данные молча.
        Проверяем, что notify() пробрасывает исключение наружу
        (чтобы OutboxProcessor мог переключиться на Kafka).
        """
        notifier = HTTPNotifier("http://bot:8000", mock_circuit_breaker)

        update = LinkUpdate(
            id=sample_link.id,
            url=str(sample_link.url),
            author="test-user",
            description="Обнаружено изменение",
            tgChatIds=[sample_link.chat_id],
        )

        with patch.object(
            notifier, "_send_request", side_effect=Exception("HTTP failed")
        ):
            with pytest.raises(Exception, match="HTTP failed"):
                await notifier.notify([update])

    @pytest.mark.asyncio
    async def test_fallback_not_silent(self, sample_link, mock_circuit_breaker):
        """
        TC-5.1: Ошибка не теряется молча.
        Проверяем, что при падении HTTP исключение содержит информацию.
        """
        notifier = HTTPNotifier("http://bot:8000", mock_circuit_breaker)

        update = LinkUpdate(
            id=sample_link.id,
            author="test-user",
            url=str(sample_link.url),
            description="Критическое уведомление",
            tgChatIds=[sample_link.chat_id],
        )

        with patch.object(
            notifier, "_send_request", side_effect=Exception("Connection refused")
        ):
            try:
                await notifier.notify([update])
            except Exception as e:
                assert "Connection refused" in str(e)
                assert update.description == "Критическое уведомление"
            else:
                pytest.fail("Должно было вылететь исключение")
