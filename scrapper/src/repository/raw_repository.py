import asyncpg
from typing import Optional
from pydantic import HttpUrl
from datetime import datetime
from contextlib import asynccontextmanager
from .base_repository import BaseRepository, db_error_handler
from models.dto.schemas import Link, GlobalLink, PaginatedLink


class ChatQueryies:
    """Класс с запросами."""

    GET_ALL_CHATS = """SELECT id FROM chats;"""

    APPEND_CHAT = """INSERT INTO chats (id) VALUES ($1) ON CONFLICT DO NOTHING;"""

    DELETE_CHAT_FROM_CHATS_LINKS_TAGS = (
        """DELETE FROM chats_links_tags WHERE chat_id = $1;"""
    )

    DELETE_CHAT_FROM_CHATS_LINKS = """DELETE FROM chats_links WHERE chat_id = $1;"""

    DELETE_CHAT = """DELETE FROM chats WHERE id = $1;"""


class LinkQueries:
    """Класс запросов для ссылок."""

    GET_ALL_LINKS_PAGINATED = """
        SELECT id, url, updated_at
        FROM links
        ORDER BY id
        LIMIT $1 OFFSET $2
    """

    GET_CHATS_FOR_LINK = """SELECT chat_id FROM chats_links WHERE link_id = $1;"""

    UPDATE_LINK_TIMESTAMP = """UPDATE links SET updated_at = $2 WHERE id = $1;"""

    GET_CHAT_LINKS_PAGINATED = """
        SELECT l.id, l.url,
        COALESCE(
            array_agg(t.name) FILTER (WHERE t.name IS NOT NULL),
            '{}'
        ) AS tags
        FROM links AS l
        JOIN chats_links AS cl ON l.id = cl.link_id
        LEFT JOIN chats_links_tags AS clt ON clt.chat_id = cl.chat_id AND clt.link_id = cl.link_id
        LEFT JOIN tags AS t ON clt.tag_id = t.id
        WHERE cl.chat_id = $1
        GROUP BY l.id, cl.chat_id
        ORDER BY l.id
        LIMIT $2 OFFSET $3;
    """

    GET_TAGS = """
        SELECT t.name
        FROM chats_links_tags AS clt
        JOIN tags AS t ON t.id = clt.tag_id
        WHERE clt.chat_id = $1 AND clt.link_id = $2;
    """

    INSERT_LINK = """INSERT INTO links (url) VALUES ($1) ON CONFLICT DO NOTHING;"""

    GET_LINK_ID = """SELECT id FROM links WHERE url = $1;"""

    INSERT_CHAT_LINK = """
        INSERT INTO chats_links (chat_id, link_id)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING;
    """

    INSERT_TAG = """INSERT INTO tags (name) VALUES ($1) ON CONFLICT DO NOTHING;"""

    GET_TAG_ID = """SELECT id FROM tags WHERE name = $1;"""

    INSERT_CHAT_LINK_TAG = """
        INSERT INTO chats_links_tags (chat_id, link_id, tag_id)
        VALUES ($1, $2, $3)
        ON CONFLICT DO NOTHING;
    """

    DELETE_CHAT_LINK_TAGS = """
        DELETE FROM chats_links_tags
        WHERE chat_id = $1 AND link_id = $2;
    """

    DELETE_CHAT_LINK = """
        DELETE FROM chats_links
        WHERE chat_id = $1 AND link_id = $2;
    """

    DELETE_LINK = """
        DELETE FROM links
        WHERE id = $1
        AND NOT EXISTS (
            SELECT 1 FROM chats_links WHERE link_id = $1
        );
    """

    EXIST_CHAT = """SELECT 1 FROM chats WHERE id = $1;"""

    EXIST_LINK = """
        SELECT 1
        FROM chats_links AS cl
        JOIN links AS l ON cl.link_id = l.id
        WHERE cl.chat_id = $1 AND l.url = $2;
    """


class RawRepository(BaseRepository):
    """Класс RAW SQL запросов."""

    def __init__(self, host: str, port: int, db: str, user: str, password: str) -> None:
        self._pool: Optional[asyncpg.Pool] = None
        self._dsn = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._dsn)
        return self._pool

    @asynccontextmanager
    async def _get_conn(self):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            yield conn

    @db_error_handler
    async def get_all_chats(self) -> set[int]:
        async with self._get_conn() as conn:
            rows = await conn.fetch(ChatQueryies.GET_ALL_CHATS)
        return {row["id"] for row in rows}

    @db_error_handler
    async def append_chat(self, chat_id: int) -> None:
        async with self._get_conn() as conn:
            await conn.execute(ChatQueryies.APPEND_CHAT, chat_id)

    @db_error_handler
    async def delete_chat(self, chat_id: int) -> None:
        async with self._get_conn() as conn:
            async with conn.transaction():
                await self._delete_chat_from_chats_links_tags(conn, chat_id)
                await self._delete_chat_from_chats_links(conn, chat_id)
                await self._delete_chat(conn, chat_id)

    async def _delete_chat_from_chats_links_tags(self, conn, chat_id: int) -> None:
        await conn.execute(ChatQueryies.DELETE_CHAT_FROM_CHATS_LINKS_TAGS, chat_id)

    async def _delete_chat_from_chats_links(self, conn, chat_id: int) -> None:
        await conn.execute(ChatQueryies.DELETE_CHAT_FROM_CHATS_LINKS, chat_id)

    async def _delete_chat(self, conn, chat_id: int) -> None:
        await conn.execute(ChatQueryies.DELETE_CHAT, chat_id)

    @db_error_handler
    async def get_all_links_paginated(
        self, page: int, limit: int
    ) -> PaginatedLink[GlobalLink]:
        async with self._get_conn() as conn:
            rows = await conn.fetch(
                LinkQueries.GET_ALL_LINKS_PAGINATED,
                limit + 1,
                page * limit,
            )

        has_next = len(rows) > limit

        links = [
            GlobalLink(id=row["id"], url=row["url"], updated_at=row["updated_at"])
            for row in rows[:limit]
        ]

        return PaginatedLink(items=links, has_next=has_next)

    @db_error_handler
    async def get_chats_for_link(self, link_id: int) -> list[int]:
        async with self._get_conn() as conn:
            rows = await conn.fetch(LinkQueries.GET_CHATS_FOR_LINK, link_id)
        return [row["chat_id"] for row in rows]

    @db_error_handler
    async def update_link_timestamp(self, link_id: int, cur_date: datetime) -> None:
        async with self._get_conn() as conn:
            await conn.execute(LinkQueries.UPDATE_LINK_TIMESTAMP, link_id, cur_date)

    @db_error_handler
    async def get_chat_links_paginated(
        self, chat_id: int, page: int, limit: int
    ) -> PaginatedLink[Link]:
        async with self._get_conn() as conn:
            rows = await conn.fetch(
                LinkQueries.GET_CHAT_LINKS_PAGINATED,
                chat_id,
                limit + 1,
                page * limit,
            )

        has_next = len(rows) > limit

        links = [
            Link(
                id=row["id"],
                url=row["url"],
                tags=row["tags"],
                chat_id=chat_id,
            )
            for row in rows[:limit]
        ]

        return PaginatedLink(items=links, has_next=has_next)

    @db_error_handler
    async def get_tags(self, chat_id: int, link_id: int) -> list[str]:
        async with self._get_conn() as conn:
            rows = await conn.fetch(LinkQueries.GET_TAGS, chat_id, link_id)
        return [row["name"] for row in rows]

    @db_error_handler
    async def append_link(self, chat_id: int, url: str, tags: list[str]) -> Link:
        async with self._get_conn() as conn:
            async with conn.transaction():
                await conn.execute(LinkQueries.INSERT_LINK, url)

                link_id = await conn.fetchval(LinkQueries.GET_LINK_ID, url)

                await conn.execute(LinkQueries.INSERT_CHAT_LINK, chat_id, link_id)

                for tag in tags:
                    await conn.execute(LinkQueries.INSERT_TAG, tag)
                    tag_id = await conn.fetchval(LinkQueries.GET_TAG_ID, tag)

                    await conn.execute(
                        LinkQueries.INSERT_CHAT_LINK_TAG,
                        chat_id,
                        link_id,
                        tag_id,
                    )

        return Link(id=link_id, chat_id=chat_id, url=HttpUrl(url), tags=tags)

    @db_error_handler
    async def delete_link(self, chat_id: int, url: str) -> Link:
        async with self._get_conn() as conn:
            async with conn.transaction():
                link_id = await conn.fetchval(LinkQueries.GET_LINK_ID, url)

                tags = await self.get_tags(chat_id, link_id)

                await conn.execute(LinkQueries.DELETE_CHAT_LINK_TAGS, chat_id, link_id)
                await conn.execute(LinkQueries.DELETE_CHAT_LINK, chat_id, link_id)
                await conn.execute(LinkQueries.DELETE_LINK, link_id)

        return Link(id=link_id, chat_id=chat_id, tags=tags, url=HttpUrl(url))

    @db_error_handler
    async def exist_chat(self, chat_id: int) -> bool:
        async with self._get_conn() as conn:
            result = await conn.fetchval(LinkQueries.EXIST_CHAT, chat_id)
        return result is not None

    @db_error_handler
    async def exist_link(self, chat_id: int, url: str) -> bool:
        async with self._get_conn() as conn:
            result = await conn.fetchval(LinkQueries.EXIST_LINK, chat_id, url)
        return result is not None
