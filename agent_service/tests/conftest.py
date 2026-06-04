import os
import sys
import httpx
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.append(str(Path(__file__).parent.parent / "src"))

os.environ["AI_TOKEN"] = "test_token"

from models.dto import LinkUpdate
from filters.words_filter import WordsFilter
from filters.author_filter import AuthorFilter
from filters.length_filter import LengthFilter
from processor import Processor
from summarizer import Summarizer


@pytest.fixture
def mock_link_update():
    return LinkUpdate(
        id=1,
        url="https://stackoverflow.com/questions/123/test",
        author="KoIvRo",
        description="Hello, world! Реклама",
        tgChatIds=[100],
    )


@pytest.fixture
def mock_link_update_with_stop_word():
    return LinkUpdate(
        id=2,
        url="https://github.com/user/repo",
        author="ValidUser",
        description="Buy cheap spam now! Limited offer!",
        tgChatIds=[100],
    )


@pytest.fixture
def mock_link_update_excluded_author():
    return LinkUpdate(
        id=3,
        url="https://github.com/bot/repo",
        author="bot-user",
        description="Automated update from CI pipeline",
        tgChatIds=[200],
    )


@pytest.fixture
def mock_link_update_short():
    return LinkUpdate(
        id=4,
        url="https://github.com/user/repo",
        author="ValidUser",
        description="Hi",
        tgChatIds=[300],
    )


@pytest.fixture
def mock_link_update_long():
    return LinkUpdate(
        id=5,
        url="https://stackoverflow.com/questions/123",
        author="ValidUser",
        description=("*" * 500),
        tgChatIds=[400],
    )


@pytest.fixture
def mock_summarizer():
    summarizer = AsyncMock()
    summarizer.summarize = AsyncMock(return_value="Short summary.")
    return summarizer


@pytest.fixture
def mock_prioritizer():
    prioritizer = MagicMock()
    prioritizer.prioritize = MagicMock(return_value="MEDIUM")
    return prioritizer


@pytest.fixture
def mock_grouper():
    grouper = AsyncMock()
    grouper.add = AsyncMock()
    return grouper


@pytest.fixture
def mock_producer():
    producer = AsyncMock()
    producer.send = AsyncMock()
    return producer


@pytest.fixture
def mock_circuit_breaker():
    cb = MagicMock()
    cb.state = "CLOSED"
    cb.call_async = AsyncMock()
    return cb


@pytest.fixture
def processor(mock_summarizer, mock_prioritizer, mock_grouper):
    """Процессор с замоканными суммаризатором, приоритизатором и группером."""
    return Processor(
        filters=[WordsFilter(), AuthorFilter(), LengthFilter()],
        summarizer=mock_summarizer,
        prioritizer=mock_prioritizer,
        grouper=mock_grouper,
    )


@pytest.fixture
def summarizer_stub(mock_circuit_breaker):
    return Summarizer(
        threshold_words=100,
        timeout=httpx.Timeout(connect=1, read=1, write=1, pool=1),
        cb=mock_circuit_breaker,
        use_ai=False,
        url="http://fake",
        model="fake",
        token="fake",
    )


@pytest.fixture
def summarizer_ai(mock_circuit_breaker):
    return Summarizer(
        threshold_words=100,
        timeout=httpx.Timeout(connect=1, read=1, write=1, pool=1),
        cb=mock_circuit_breaker,
        use_ai=True,
        url="http://fake",
        model="fake",
        token="fake",
    )
