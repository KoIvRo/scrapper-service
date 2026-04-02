import logging
from logging import Logger


def setup_logger(name: str) -> Logger:
    """Настройка логгера."""

    class ExtraFormatter(logging.Formatter):
        def format(self, record):
            base_msg = super().format(record)

            extra = []
            if hasattr(record, "user_id"):
                extra.append(f"user_id={record.user_id}")
            if hasattr(record, "username"):
                extra.append(f"username={record.username}")
            if hasattr(record, "command"):
                extra.append(f"command={record.command}")

            if extra:
                return f"{base_msg} {' '.join(extra)}"
            return base_msg

    formatter = ExtraFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[handler])

    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    return logging.getLogger(name)
