import pytest
from models.schemas import LinkUpdate
from unittest.mock import MagicMock


class TestKafkaConsumer:
    """Тесты для Kafka консьюмера."""

    @pytest.mark.asyncio
    async def test_process_valid_message(self, kafka_consumer, mock_handle_update):
        """Тест успешной обработки валидного сообщения."""
        update = LinkUpdate(
            updated_id="test-uuid-1",
            id=1,
            url="https://github.com/user/repo",
            description="Test update",
            tgChatIds=[123],
        )

        kafka_consumer._avro_deserializer = MagicMock(return_value=update)

        message = MagicMock()
        message.error.return_value = None
        message.value.return_value = b"fake-bytes"

        kafka_consumer._consumer.poll = MagicMock(
            side_effect=[message, KeyboardInterrupt()]
        )

        try:
            await kafka_consumer.start()
        except KeyboardInterrupt:
            pass

        mock_handle_update.assert_called_once_with(update)
        assert "test-uuid-1" in kafka_consumer._processed_id

    @pytest.mark.asyncio
    async def test_skip_duplicate_message(self, kafka_consumer, mock_handle_update):
        """Тест пропуска дубликата сообщения."""
        update = LinkUpdate(
            updated_id="test-uuid-2",
            id=2,
            url="https://github.com/user/repo2",
            description="Test update 2",
            tgChatIds=[456],
        )

        kafka_consumer._processed_id.add("test-uuid-2")
        kafka_consumer._avro_deserializer = MagicMock(return_value=update)

        message = MagicMock()
        message.error.return_value = None
        message.value.return_value = b"fake-bytes"

        kafka_consumer._consumer.poll = MagicMock(
            side_effect=[message, KeyboardInterrupt()]
        )

        try:
            await kafka_consumer.start()
        except KeyboardInterrupt:
            pass

        mock_handle_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_deserialization_error(self, kafka_consumer, mock_handle_update):
        """Тест ошибки десериализации."""
        kafka_consumer._avro_deserializer = MagicMock(
            side_effect=Exception("Deserialization failed")
        )

        message = MagicMock()
        message.error.return_value = None
        message.value.return_value = b"bad-bytes"

        kafka_consumer._consumer.poll = MagicMock(
            side_effect=[message, KeyboardInterrupt()]
        )

        try:
            await kafka_consumer.start()
        except KeyboardInterrupt:
            pass

        mock_handle_update.assert_not_called()
