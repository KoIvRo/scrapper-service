import json
from models.dto.schemas import PaginatedLink, Link
from redis.asyncio import RedisCluster
from typing import Optional
import logging

logger = logging.getLogger()


class CacheManager:
    """Управление кэшом."""

    def __init__(self, port: str, host: int, ttl: int) -> None:
        self._client = RedisCluster(host=host, port=port)
        self._ttl = ttl

    async def get_cache_links(
        self, chat_id: int, page: int, limit: int
    ) -> Optional[PaginatedLink[Link]]:
        """Получить кэш для GET."""
        key = self._create_key_links(chat_id, page, limit)

        data = await self._client.get(key)

        if data:
            logger.info("Cache found", extra={"chat_id": chat_id})
            return self._parse_json_to_paginated_link(data)

        return None

    async def save_cache_links(
        self, chat_id: int, page: int, limit: int, paginated_link: PaginatedLink[Link]
    ) -> None:
        """Сохранить кэш."""

        key = self._create_key_links(chat_id, page, limit)

        data = self._parse_paginated_link_to_json(paginated_link)

        await self._client.set(key, data)
        await self._client.expire(key, self._ttl)

        logger.info("Cache saved", extra={"chat_id": chat_id})

    async def delete_cache_links(self, chat_id: int) -> None:
        """Удалить весь кэш затронутого чата."""

        keys = await self._client.keys(f"links:{chat_id}:*:*")

        if keys:
            await self._client.delete(*keys)
            logger.info("Cache deleted", extra={"chat_id": chat_id})

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
