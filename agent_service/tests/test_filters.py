import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.append(str(Path(__file__).parent.parent / "src"))

from filters.author_filter import AuthorFilter
from filters.words_filter import WordsFilter
from filters.length_filter import LengthFilter


class TestAuthorFilter:
    """Тест фильтров по автору."""

    def test_canceled_author_filters(self, mock_link_update):
        """Если True, отбрасываем update."""
        with patch("filters.author_filter.settings") as mock_settings:
            mock_settings.filters.authors = ["KoIvRo"]
            assert AuthorFilter.filter(mock_link_update) == True

    def test_empty_author_filters(self, mock_link_update):
        """С пустым списком авторов."""
        with patch("filters.author_filter.settings") as mock_settings:
            mock_settings.filters.authors = []
            assert AuthorFilter.filter(mock_link_update) == False

    def test_accepted_author_filters(self, mock_link_update):
        """Обновление прошло фильтр, False."""
        with patch("filters.author_filter.settings") as mock_settings:
            mock_settings.filters.authors = ["Unknown"]
            assert AuthorFilter.filter(mock_link_update) == False


class TestWordFilter:
    """Тест фильтров по стоп словам."""

    def test_canceled_filters(self, mock_link_update):
        """Отнокление по стоп словам."""
        with patch("filters.words_filter.settings") as mock_settings:
            mock_settings.filters.stop_words = ["реклама"]
            assert WordsFilter.filter(mock_link_update) == True

    def test_empty_filters(self, mock_link_update):
        """Пустой список."""
        with patch("filters.words_filter.settings") as mock_settings:
            mock_settings.filters.stop_words = []
            assert WordsFilter.filter(mock_link_update) == False

    def test_accepted_filters(self, mock_link_update):
        """Пустой список."""
        with patch("filters.words_filter.settings") as mock_settings:
            mock_settings.filters.stop_words = ["промо"]
            assert WordsFilter.filter(mock_link_update) == False


class TestLengthFilter:
    """Тест по длине описания."""

    def test_cancelled_filters(self, mock_link_update):
        """Отколение в связи с малой длиной сообщения."""
        with patch("filters.length_filter.settings") as mock_settings:
            mock_settings.filters.min_length = 100
            assert LengthFilter.filter(mock_link_update) == True

    def test_accepted_filters(self, mock_link_update):
        """Отколение в связи с малой длиной сообщения."""
        with patch("filters.length_filter.settings") as mock_settings:
            mock_settings.filters.min_length = 1
            assert LengthFilter.filter(mock_link_update) == False
