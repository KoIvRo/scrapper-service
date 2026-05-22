import sys
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).parent.parent / "src"))

from processor import Processor


class TestProcessorFiltering:
    """Тесты фильтрации (TC-2.1 – TC-2.4)."""

    @pytest.mark.asyncio
    async def test_filter_by_stop_word(
        self, processor, mock_link_update_with_stop_word
    ):
        """TC-2.1: Обновление со стоп-словом игнорируется."""
        with patch("filters.words_filter.settings") as mock_settings:
            mock_settings.filters.stop_words = ["spam"]
            result = await processor.process_update(mock_link_update_with_stop_word)
            assert result is None

    @pytest.mark.asyncio
    async def test_filter_by_author(self, processor, mock_link_update_excluded_author):
        """TC-2.2: Обновление от исключённого автора игнорируется."""
        with patch("filters.author_filter.settings") as mock_settings:
            mock_settings.filters.authors = ["bot-user"]
            result = await processor.process_update(mock_link_update_excluded_author)
            assert result is None

    @pytest.mark.asyncio
    async def test_filter_by_min_length(self, processor, mock_link_update_short):
        """TC-2.3: Короткое обновление игнорируется."""
        with patch("filters.length_filter.settings") as mock_settings:
            mock_settings.filters.min_length = 10
            result = await processor.process_update(mock_link_update_short)
            assert result is None

    @pytest.mark.asyncio
    async def test_valid_update_passes_all_filters(self, processor, mock_link_update):
        """TC-2.4: Валидное обновление проходит все фильтры."""
        with (
            patch("filters.words_filter.settings") as words_settings,
            patch("filters.author_filter.settings") as author_settings,
            patch("filters.length_filter.settings") as length_settings,
        ):
            words_settings.filters.stop_words = ["spam"]
            author_settings.filters.authors = ["bot-user"]
            length_settings.filters.min_length = 10

            result = await processor.process_update(mock_link_update)

            assert result is not None
            assert result.id == mock_link_update.id
            assert result.author == mock_link_update.author
            assert result.tgChatIds == mock_link_update.tgChatIds


class TestProcessorSummarization:
    """Тесты суммаризации (TC-3.1, TC-3.2)."""

    @pytest.fixture
    def processor_with_stub(self):
        """Процессор с реальным Summarizer с минимальными параметрами."""
        import httpx
        from summarizer import Summarizer
        from unittest.mock import MagicMock

        summarizer = Summarizer(
            threshold_words=100,
            timeout=httpx.Timeout(connect=1, read=1, write=1, pool=1),
            cb=MagicMock(),
            use_ai=False,
            url="http://fake",
            model="fake",
            token="fake",
        )
        return Processor(filters=[], summarizer=summarizer)

    @pytest.fixture
    def processor_with_mock(self, mock_summarizer):
        """Процессор с замоканным суммаризатором."""
        return Processor(filters=[], summarizer=mock_summarizer)

    @pytest.mark.asyncio
    async def test_summarize_long_text(
        self, processor_with_stub, mock_link_update_long
    ):
        """TC-3.1: Длинный текст суммаризируется (stub-режим)."""
        result = await processor_with_stub.process_update(mock_link_update_long)

        assert result is not None
        assert result.description != mock_link_update_long.description
        assert result.description.endswith("...")
        assert len(result.description) == 103  # 100 + "..."

    @pytest.mark.asyncio
    async def test_short_text_not_summarized(
        self, processor_with_stub, mock_link_update
    ):
        """TC-3.2: Короткий текст не суммаризируется."""
        result = await processor_with_stub.process_update(mock_link_update)

        assert result is not None
        assert result.description == mock_link_update.description

    @pytest.mark.asyncio
    async def test_summarizer_called_for_long_text(
        self, processor_with_mock, mock_link_update_long, mock_summarizer
    ):
        """Суммаризатор вызван для длинного текста."""
        await processor_with_mock.process_update(mock_link_update_long)
        mock_summarizer.summarize.assert_called_once_with(
            mock_link_update_long.description
        )
