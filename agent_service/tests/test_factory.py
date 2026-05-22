import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from dependencies.summarizer_factory import get_summarizer
from summarizer import Summarizer
from dependencies.processor_factory import get_processor
from processor import Processor


class TestProcessorFactory:
    """Тесты ProcessorFactory."""

    def test_get_processor_returns_processor(self):
        """Фабрика возвращает Processor."""

        processor = get_processor()
        assert isinstance(processor, Processor)

    def test_get_processor_returns_same_instance(self):
        """Фабрика возвращает один и тот же экземпляр (синглтон)."""

        p1 = get_processor()
        p2 = get_processor()
        assert p1 is p2


class TestSummarizerFactory:
    """Тесты SummarizerFactory."""

    def test_get_summarizer_returns_summarizer(self):
        """Фабрика возвращает Summarizer."""

        summarizer = get_summarizer()
        assert isinstance(summarizer, Summarizer)

    def test_get_summarizer_returns_same_instance(self):
        """Фабрика возвращает один и тот же экземпляр (синглтон)."""

        s1 = get_summarizer()
        s2 = get_summarizer()
        assert s1 is s2
