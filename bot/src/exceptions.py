class BotException(Exception):
    """Базовый класс ошибки."""


class ClientException(BotException):
    """Ошибка клиента."""

    message = "Произошла ошибка клиента.\nПопробуйте еще раз."
