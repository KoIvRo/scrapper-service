import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import httpx

sys.path.append(str(Path(__file__).parent.parent / "src"))

from summarizer import Summarizer


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
        """Длинный текст обрезается."""
        long_text = "A" * 150
        result = await summarizer_stub.summarize(long_text)
        assert result == "A" * 100 + "..."
        assert len(result) == 103

    @pytest.mark.asyncio
    async def test_ai_success(self, summarizer_ai, mock_circuit_breaker):
        """AI вернул ответ."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "AI summary."}}]
        }
        mock_circuit_breaker.call_async.return_value = mock_response

        result = await summarizer_ai.summarize("A" * 150)
        assert result == "AI summary."

    @pytest.mark.asyncio
    async def test_ai_error_fallback(self, summarizer_ai, mock_circuit_breaker):
        """Ошибка AI → stub."""
        mock_circuit_breaker.call_async.side_effect = Exception("API error")

        result = await summarizer_ai.summarize("A" * 150)
        assert result == "A" * 100 + "..."

    @pytest.mark.asyncio
    async def test_cb_open_uses_stub(self, summarizer_ai, mock_circuit_breaker):
        """CB OPEN → stub без запроса."""
        mock_circuit_breaker.state = "OPEN"

        result = await summarizer_ai.summarize("A" * 150)
        assert result == "A" * 100 + "..."
        mock_circuit_breaker.call_async.assert_not_called()

    @pytest.mark.asyncio
    async def test_ai_500_fallback(self, summarizer_ai, mock_circuit_breaker):
        """AI вернул 500 → stub."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_circuit_breaker.call_async.return_value = mock_response

        result = await summarizer_ai.summarize("A" * 150)
        assert result == "A" * 100 + "..."
