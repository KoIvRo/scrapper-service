import logging
from pythonjsonlogger.json import JsonFormatter
from config import settings


def init_logger() -> None:
    """Настройка логгера ВЫЗЫВАТЬ ПРИ СТАРТЕ."""
    logger = logging.getLogger()
    formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    log_handler: logging.Handler

    if settings.logger_output == "stdout":
        log_handler = logging.StreamHandler()
    else:
        log_handler = logging.FileHandler(settings.logger_output, encoding="utf-8")

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.setLevel(settings.logger_level)

    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
