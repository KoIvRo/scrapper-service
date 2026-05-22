import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))
from models.dto.schemas import LinkUpdate


class TestKafkaNotifier:
    """Тесты для Kafka нотифаера."""

    @pytest.mark.asyncio
    async def test_notify_sends_messages(self, kafka_notifier, sample_updates):
        """Тест отправки уведомлений."""
        await kafka_notifier.notify(sample_updates)

        assert kafka_notifier._producer.produce.call_count == 2
        kafka_notifier._producer.produce.assert_any_call(
            "test-topic", b"fake-avro-bytes"
        )
        kafka_notifier._producer.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_empty_list(self, kafka_notifier):
        """Тест отправки пустого списка."""
        await kafka_notifier.notify([])

        kafka_notifier._producer.produce.assert_not_called()
        kafka_notifier._producer.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_single_update(self, kafka_notifier):
        """Тест отправки одного уведомления."""
        update = LinkUpdate(
            updated_id="uuid-3",
            id=3,
            author="test-user",
            url="https://github.com/user/repo3",
            description="Single update",
            tgChatIds=[789],
        )

        await kafka_notifier.notify([update])

        kafka_notifier._producer.produce.assert_called_once_with(
            "test-topic", b"fake-avro-bytes"
        )
        kafka_notifier._producer.flush.assert_called_once()
