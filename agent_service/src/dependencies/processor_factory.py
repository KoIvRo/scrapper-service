from processor import Processor
from filters.author_filter import AuthorFilter
from filters.words_filter import WordsFilter
from filters.length_filter import LengthFilter


class ProcessorFactory:
    """Фабрика для Processor."""

    def __init__(self) -> None:
        self._processor = None

    def get_processor(self) -> Processor:
        """Получить processor."""

        if self._processor is None:
            self._processor = Processor(
                [AuthorFilter, LengthFilter, WordsFilter]
            )
        
        return self._processor
    
processor_factory = ProcessorFactory()

def get_processor() -> Processor:
    """Получить Processor."""

    return processor_factory.get_processor()
