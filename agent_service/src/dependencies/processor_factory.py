from processor import Processor
from filters.author_filter import AuthorFilter
from filters.words_filter import WordsFilter
from filters.length_filter import LengthFilter
from .summarizer_factory import get_summarizer
from .prioritizer_factory import get_prioritizer


class ProcessorFactory:
    """Фабрика для Processor."""

    def __init__(self) -> None:
        self._processor = None

    def get_processor(self) -> Processor:
        """Получить processor."""

        if self._processor is None:
            self._processor = Processor(
                [AuthorFilter(), LengthFilter(), WordsFilter()],
                summarizer=get_summarizer(),
                prioritizer=get_prioritizer(),
            )

        return self._processor


processor_factory = ProcessorFactory()


def get_processor() -> Processor:
    """Получить Processor."""

    return processor_factory.get_processor()
