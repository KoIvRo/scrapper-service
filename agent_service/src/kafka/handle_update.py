from dependencies.processor_factory import get_processor
from models.dto import LinkUpdate


async def handle_update(update: LinkUpdate) -> None:
    """Обработка обновления через Processor."""

    processor = get_processor()

    await processor.process_update(update)
