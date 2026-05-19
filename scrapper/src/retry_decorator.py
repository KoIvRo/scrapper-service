import httpx
from config import settings
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_any,
    retry_if_exception_type,
)
from tenacity import retry_if_exception


def is_retryable_http_error(exception: BaseException) -> bool:
    """Проверка: является ли ошибка HTTP с нужным статусом."""
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in settings.retryable_status_codes
    return False


retry_decorator = retry(
    stop=stop_after_attempt(settings.retry_max_attempts),
    wait=wait_exponential(
        multiplier=settings.retry_exponential_multiplier,
        min=settings.retry_exponential_min_seconds,
        max=settings.retry_exponential_max_seconds,
    ),
    retry=retry_any(
        retry_if_exception(is_retryable_http_error),
        retry_if_exception_type(
            (
                httpx.TimeoutException,
                httpx.ConnectError,
                httpx.RemoteProtocolError,
            )
        ),
    ),
    reraise=True,
)
