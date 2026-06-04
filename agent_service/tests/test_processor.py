import httpx
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.append(str(Path(__file__).parent.parent / "src"))

from processor import Processor
from summarizer import Summarizer
from prioritizer import Prioritizer


class TestProcessorFiltering:
    """Тесты фильтрации (TC-2.1 – TC-2.4)."""

    @pytest.mark.asyncio
    async def test_filter_by_stop_word(self, processor, mock_link_update_with_stop_word):
        with patch("filters.words_filter.settings") as mock_settings:
            mock_settings.filters.stop_words = ["spam"]
            await processor.process_update(mock_link_update_with_stop_word)
            # С фильтром — grouper.add не вызывается
            processor._grouper.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_filter_by_author(self, processor, mock_link_update_excluded_author):
        with patch("filters.author_filter.settings") as mock_settings:
            mock_settings.filters.authors = ["bot-user"]
            await processor.process_update(mock_link_update_excluded_author)
            processor._grouper.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_filter_by_min_length(self, processor, mock_link_update_short):
        with patch("filters.length_filter.settings") as mock_settings:
            mock_settings.filters.min_length = 10
            await processor.process_update(mock_link_update_short)
            processor._grouper.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_valid_update_passes_all_filters(self, processor, mock_link_update):
        with (
            patch("filters.words_filter.settings") as words_settings,
            patch("filters.author_filter.settings") as author_settings,
            patch("filters.length_filter.settings") as length_settings,
        ):
            words_settings.filters.stop_words = ["spam"]
            author_settings.filters.authors = ["bot-user"]
            length_settings.filters.min_length = 10

            await processor.process_update(mock_link_update)
            processor._grouper.add.assert_called_once()


class TestProcessorSummarization:
    """Тесты суммаризации (TC-3.1, TC-3.2)."""

    @pytest.fixture
    def processor_with_stub(self):

        summarizer = Summarizer(
            threshold_words=100,
            timeout=httpx.Timeout(connect=1, read=1, write=1, pool=1),
            cb=MagicMock(), use_ai=False,
            url="http://fake", model="fake", token="fake",
        )
        return Processor(
            filters=[],
            summarizer=summarizer,
            prioritizer=Prioritizer(low_words=["minor"], high_words=["critical"]),
            grouper=AsyncMock(),
        )

    @pytest.mark.asyncio
    async def test_short_text_not_summarized(self, processor_with_stub, mock_link_update):
        await processor_with_stub.process_update(mock_link_update)

        call_args = processor_with_stub._grouper.add.call_args
        processed = call_args[0][0]
        assert processed.description == mock_link_update.description
