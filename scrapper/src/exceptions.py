class ScrapperServiceError(Exception):
    """Общий класс ошибок scrapper service."""

    status_code = 500
    message = "Server error"


class LinkServiceError(Exception):
    """Класс ошибок LinkService."""

    status_code = 400
    message = "Bad request"


class ExistChatError(LinkServiceError):
    """Класс ошибка чат уже существует."""

    status_code = 409
    message = "Chat already exists"


class UnknownChatError(LinkServiceError):
    """Ошибка чат не найден."""

    status_code = 404
    message = "Unknown chat"


class ExistLink(LinkServiceError):
    """Ошибка дубликат ссылки."""

    status_code = 409
    message = "Link already exists"


class UnknownLink(LinkServiceError):
    """Ошибка неизвестная ссылка."""

    status_code = 404
    message = "Unknown links"


class InvalidURL(LinkServiceError):
    """Невалидный url."""

    status_code = 400
    message = "Invalid url"


class InvalidPage(LinkServiceError):
    """Невалидные данные о странице."""

    status_code = 400
    message = "Invalid page number"


class InvalidLimit(LinkServiceError):
    """Невалидные данные о лимите."""

    status_code = 400
    message = "Invalid limit for links"


class DataBaseError(ScrapperServiceError):
    """Ошибка в работе базы данных."""

    status_code = 500
    message = "Internal server error"
