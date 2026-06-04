import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock
import httpx

sys.path.append(str(Path(__file__).parent.parent / "src"))


class TestSummarizer:
    """Тесты суммаризатора."""

    @pytest.mark.asyncio
    async def test_short_text_not_summarized_stub(self, summarizer_stub):
        """Короткий текст не меняется (stub)."""
        text = "Short text."
        result = await summarizer_stub.summarize(text)
        assert result == text

    @pytest.mark.asyncio
    async def test_short_text_not_summarized_ai(self, summarizer_ai):
        """Короткий текст не меняется (AI-режим)."""
        text = "Short text."
        result = await summarizer_ai.summarize(text)
        assert result == text

    @pytest.mark.asyncio
    async def test_long_text_shortened_stub(self, summarizer_stub):
        """Длинный текст обрезается по словам."""
        long_text = "word1 word2 word3 word4 word5 " * 30
        result = await summarizer_stub.summarize(long_text)

        expected_words = (["word1", "word2", "word3", "word4", "word5"] * 30)[:100]
        expected = " ".join(expected_words) + "..."
        assert result == expected

    @pytest.mark.asyncio
    async def test_ai_success(self, summarizer_ai, mock_circuit_breaker):
        """AI вернул ответ."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "AI summary."}}]
        }
        mock_circuit_breaker.call_async.return_value = mock_response

        long_text = "word " * 150
        result = await summarizer_ai.summarize(long_text)
        assert result == "AI summary."

    @pytest.mark.asyncio
    async def test_ai_error_fallback(self, summarizer_ai, mock_circuit_breaker):
        """Ошибка AI → stub."""
        mock_circuit_breaker.call_async.side_effect = Exception("API error")

        long_text = "hello " * 150
        result = await summarizer_ai.summarize(long_text)

        expected = " ".join(["hello"] * 100) + "..."
        assert result == expected

    @pytest.mark.asyncio
    async def test_cb_open_uses_stub(self, summarizer_ai, mock_circuit_breaker):
        """CB OPEN → stub без запроса."""
        mock_circuit_breaker.state = "OPEN"

        long_text = "test " * 150
        result = await summarizer_ai.summarize(long_text)

        expected = " ".join(["test"] * 100) + "..."
        assert result == expected
        mock_circuit_breaker.call_async.assert_not_called()

    @pytest.mark.asyncio
    async def test_ai_500_fallback(self, summarizer_ai, mock_circuit_breaker):
        """AI вернул 500 → stub."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_circuit_breaker.call_async.return_value = mock_response

        long_text = "word " * 150
        result = await summarizer_ai.summarize(long_text)

        expected = " ".join(["word"] * 100) + "..."
        assert result == expected
