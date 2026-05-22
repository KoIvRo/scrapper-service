import httpx
from typing import Optional


class Summarizer:
    """Класс саммарайзер уведомлений."""

    def __init__(self, threshold_words: int, timeout: httpx.Timeout, use_ai: bool, url: str, model: str, token) -> None:
        self._client: Optional[httpx.AsyncClient] = None
        self._timeout = timeout
        self._use_ai = use_ai
        self._threshold_words = threshold_words
        self._url = url
        self._model = model
        self._token = token


    async def _get_client(self) -> httpx.AsyncClient:
        """Получить клиента."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self._timeout, follow_redirects=True,)
        return self._client

    async def summarize(self, description: str) -> str:
        """Сжатие текста (пока stub)."""

        if not self._is_need(len(description)):
            return description

        elif not self._use_ai:
            return f"{description[:self._threshold_words]}..."
        
        return await self._make_request(description)
        
    
    async def _make_request(self, description: str) -> str:
        """Сделать запрос к API."""

        client = await self._get_client()

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Summary in 2-3 sentences {description}"
                }
            ],
            "model": self._model
        }

        response = await client.post(self._url, headers=headers, json=payload)

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _is_need(self, len_description: int) -> bool:
        """Нужна ли саммаризация."""
        return len_description > self._threshold_words
