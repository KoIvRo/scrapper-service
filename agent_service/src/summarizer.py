import httpx
from aiobreaker import CircuitBreaker
from retry_decorator import retry
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Summarizer:
    """Класс саммарайзер уведомлений."""

    def __init__(
        self,
        threshold_words: int,
        timeout: httpx.Timeout,
        cb: CircuitBreaker,
        use_ai: bool,
        url: str,
        model: str,
        token: str,
    ) -> None:
        self._client: Optional[httpx.AsyncClient] = None
        self._timeout = timeout
        self._use_ai = use_ai
        self._threshold_words = threshold_words
        self._url = url
        self._model = model
        self._token = token
        self._cb = cb

    async def _get_client(self) -> httpx.AsyncClient:
        """Получить клиента."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
            )
        return self._client

    async def summarize(self, description: str) -> str:
        """Сжатие текста (пока stub)."""

        if not self._is_need(len(description)):
            return description

        elif not self._use_ai or self._cb.state == "OPEN":
            return self._shorten(description)

        return await self._make_request(description)

    async def _make_request(self, description: str) -> str:
        """Сделать запрос к API."""

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messages": [
                {"role": "user", "content": f"Summary in 2-3 sentences {description}"}
            ],
            "model": self._model,
        }

        try:
            response: httpx.Response = await self._cb.call_async(
                self._post,
                headers=headers,
                payload=payload,
            )

            if response.status_code == 200:
                return self._parse_response(response)
            else:
                return self._shorten(description)
        except Exception as e:
            logger.warning("AI API error", extra={"error": e})
            return self._shorten(description)

    @retry
    async def _post(self, headers, payload) -> httpx.Response:
        """Метод для вызова post под декоратором."""

        client = await self._get_client()
        response = await client.post(self._url, headers=headers, json=payload)
        response.raise_for_status()
        return response

    def _parse_response(self, response: httpx.Response) -> str:
        """Распрасить ответ от API."""
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _shorten(self, description: str) -> str:
        """Укоротить сообщение."""
        return f"{description[:self._threshold_words]}..."

    def _is_need(self, len_description: int) -> bool:
        """Нужна ли саммаризация."""
        return len_description > self._threshold_words
