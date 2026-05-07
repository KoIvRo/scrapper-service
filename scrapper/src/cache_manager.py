import json
from models.dto.schemas import PaginatedLink, Link
from redis.asyncio import Redis
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Управление кэшом."""

    def __init__(self, host: str, port: int, ttl: int) -> None:
        self._client = Redis(host=host, port=port, decode_responses=True)
        self._ttl = ttl
        self._cache: dict[str, PaginatedLink[Link]] = {}

    async def get_cache_links(
        self, chat_id: int, page: int, limit: int
    ) -> Optional[PaginatedLink[Link]]:
        """Получить кэш для GET."""

        try:
            key = self._create_key_links(chat_id, page, limit)

            if key in self._cache:
                return self._cache[key]

            data = await self._client.get(key)

            if data:
                logger.info("Cache found", extra={"chat_id": chat_id})
                paginated_link = self._parse_json_to_paginated_link(data)
                self._cache[key] = paginated_link
                return paginated_link

            return None
        except Exception as e:
            logger.warning("Error in valkey", extra={"error": e})
            return None

    async def save_cache_links(
        self, chat_id: int, page: int, limit: int, paginated_link: PaginatedLink[Link]
    ) -> None:
        """Сохранить кэш."""

        try:
            key = self._create_key_links(chat_id, page, limit)

            self._cache[key] = paginated_link

            data = self._parse_paginated_link_to_json(paginated_link)

            await self._client.set(key, data)
            await self._client.expire(key, self._ttl)

            logger.info("Cache saved", extra={"chat_id": chat_id})
        except Exception as e:
            logger.warning("Error in valkey", extra={"error": e})

    async def delete_cache_links(self, chat_id: int) -> None:
        """Удалить весь кэш затронутого чата."""
        await self._delete_valkey_links(chat_id)
        self._delete_local_links(chat_id)

    async def _delete_valkey_links(self, chat_id: int) -> None:
        """Удалить старый кэш из valkey."""
        try:
            keys = await self._client.keys(f"links:{chat_id}:*:*")

            if keys:
                await self._client.delete(*keys)
                logger.info("Cache deleted", extra={"chat_id": chat_id})
        except Exception as e:
            logger.warning("Error in valkey", extra={"error": e})

    def _delete_local_links(self, chat_id: int) -> None:
        """Удалить старый кэш из _cache."""
        try:
            keys_to_delete = [
                k for k in self._cache if k.startswith(f"links:{chat_id}:")
            ]
            for k in keys_to_delete:
                del self._cache[k]
        except Exception as e:
            logger.warning("Error in delete key", extra={"error": e})

    def _parse_paginated_link_to_json(self, paginated_link: PaginatedLink[Link]) -> str:
        """Превратить PaginatedLink в json."""

        return json.dumps(
            {
                "items": [
                    link.model_dump(mode="json") for link in paginated_link.items
                ],
                "has_next": paginated_link.has_next,
            }
        )

    def _parse_json_to_paginated_link(self, data: str) -> PaginatedLink[Link]:
        """Превратить json в PaginatedLink."""
        cached = json.loads(data)
        return PaginatedLink(
            items=[Link(**item) for item in cached["items"]],
            has_next=cached["has_next"],
        )

    def _create_key_links(self, chat_id: int, page: int, limit: int) -> str:
        """Создать ключ для записи."""

        return f"links:{chat_id}:{page}:{limit}"
