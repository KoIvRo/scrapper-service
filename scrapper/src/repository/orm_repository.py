from models.dto.schemas import Link, GlobalLink, PaginatedLink
from models.orm.schemas import Chat, Link as LinkORM, Tag, ChatLink, ChatLinkTag
from pydantic import HttpUrl
from logger_config import setup_logger
from .base_repository import BaseRepository, db_error_handler
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, update, delete, func, exists
from sqlalchemy.dialects.postgresql import insert


logger = setup_logger(__name__)


class OrmRepository(BaseRepository):
    """ORM имплементация репозитория."""

    def __init__(self, host: str, port: int, db: str, user: str, password: str) -> None:
        self._dsn = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

        self.engine = create_async_engine(self._dsn, echo=False)

        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    def _build_tags_map(self, rows) -> dict[int, list[str]]:
        tags_map: dict[int, list[str]] = {}
        for link_id, tag_name in rows:
            tags_map.setdefault(link_id, []).append(tag_name)
        return tags_map

    @db_error_handler
    async def get_all_chats(self) -> set[int]:
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(select(Chat.id))
            return {row[0] for row in result.all()}

    @db_error_handler
    async def append_chat(self, chat_id: int) -> None:
        async with self.AsyncSessionLocal() as session:
            await session.execute(
                insert(Chat).values(id=chat_id).on_conflict_do_nothing()
            )
            await session.commit()

    @db_error_handler
    async def delete_chat(self, chat_id: int) -> None:
        async with self.AsyncSessionLocal() as session:
            await session.execute(delete(Chat).where(Chat.id == chat_id))
            await session.commit()

    @db_error_handler
    async def get_all_links(self) -> list[GlobalLink]:
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                select(LinkORM.id, LinkORM.url, LinkORM.updated_at)
            )

            return [
                GlobalLink(id=row.id, url=row.url, updated_at=row.updated_at)
                for row in result.all()
            ]

    @db_error_handler
    async def get_all_links_paginated(
        self, page: int, limit: int
    ) -> PaginatedLink[GlobalLink]:
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                select(LinkORM)
                .order_by(LinkORM.id)
                .limit(limit + 1)
                .offset(page * limit)
            )

            rows = result.scalars().all()

        has_next = len(rows) > limit

        return PaginatedLink(
            items=[
                GlobalLink(id=row.id, url=row.url, updated_at=row.updated_at)
                for row in rows[:limit]
            ],
            has_next=has_next,
        )

    @db_error_handler
    async def get_chat_links_paginated(
        self, chat_id: int, page: int, limit: int
    ) -> PaginatedLink[Link]:
        async with self.AsyncSessionLocal() as session:
            links_result = await session.execute(
                select(LinkORM.id, LinkORM.url)
                .join(ChatLink, ChatLink.link_id == LinkORM.id)
                .where(ChatLink.chat_id == chat_id)
                .order_by(LinkORM.id)
                .limit(limit + 1)
                .offset(page * limit)
            )

            rows = links_result.all()

            tag_rows = await session.execute(
                select(ChatLinkTag.link_id, Tag.name)
                .join(Tag, Tag.id == ChatLinkTag.tag_id)
                .where(ChatLinkTag.chat_id == chat_id)
            )

        has_next = len(rows) > limit
        tags_map = self._build_tags_map(tag_rows.all())

        return PaginatedLink(
            items=[
                Link(
                    id=row.id,
                    url=row.url,
                    tags=tags_map.get(row.id, []),
                    chat_id=chat_id,
                )
                for row in rows[:limit]
            ],
            has_next=has_next,
        )

    @db_error_handler
    async def get_chat_links(self, chat_id: int) -> list[Link]:
        async with self.AsyncSessionLocal() as session:
            links_result = await session.execute(
                select(LinkORM.id, LinkORM.url)
                .join(ChatLink, ChatLink.link_id == LinkORM.id)
                .where(ChatLink.chat_id == chat_id)
            )

            tag_rows = await session.execute(
                select(ChatLinkTag.link_id, Tag.name)
                .join(Tag, Tag.id == ChatLinkTag.tag_id)
                .where(ChatLinkTag.chat_id == chat_id)
            )

        links = links_result.all()
        tags_map = self._build_tags_map(tag_rows.all())

        return [
            Link(
                id=link.id,
                url=link.url,
                tags=tags_map.get(link.id, []),
                chat_id=chat_id,
            )
            for link in links
        ]

    @db_error_handler
    async def append_link(self, chat_id: int, url: str, tags: list[str]) -> Link:
        async with self.AsyncSessionLocal() as session:
            async with session.begin():
                row_link_id = await session.execute(
                    insert(LinkORM)
                    .values(url=url)
                    .on_conflict_do_update(
                        index_elements=[LinkORM.url],
                        set_={"url": url},
                    )
                    .returning(LinkORM.id)
                )

                link_id = row_link_id.scalar_one()

                await session.execute(
                    insert(ChatLink)
                    .values(chat_id=chat_id, link_id=link_id)
                    .on_conflict_do_nothing()
                )

                for tag in tags:
                    row_tag_id = await session.execute(
                        insert(Tag)
                        .values(name=tag)
                        .on_conflict_do_update(
                            index_elements=[Tag.name],
                            set_={"name": tag},
                        )
                        .returning(Tag.id)
                    )

                    tag_id = row_tag_id.scalar_one()

                    await session.execute(
                        insert(ChatLinkTag).values(
                            chat_id=chat_id,
                            link_id=link_id,
                            tag_id=tag_id,
                        )
                    )

        return Link(
            id=link_id,
            url=HttpUrl(url),
            chat_id=chat_id,
            tags=tags,
        )

    @db_error_handler
    async def delete_link(self, chat_id: int, url: str) -> Link:
        async with self.AsyncSessionLocal() as session:
            async with session.begin():
                link_id = (
                    await session.execute(select(LinkORM.id).where(LinkORM.url == url))
                ).scalar_one()

                tag_rows = await session.execute(
                    select(Tag.name)
                    .join(ChatLinkTag, ChatLinkTag.tag_id == Tag.id)
                    .where(
                        ChatLinkTag.chat_id == chat_id,
                        ChatLinkTag.link_id == link_id,
                    )
                )

                tags = [row[0] for row in tag_rows.all()]

                await session.execute(
                    delete(ChatLinkTag).where(
                        ChatLinkTag.chat_id == chat_id,
                        ChatLinkTag.link_id == link_id,
                    )
                )

                await session.execute(
                    delete(ChatLink).where(
                        ChatLink.chat_id == chat_id,
                        ChatLink.link_id == link_id,
                    )
                )

                count = await session.execute(
                    select(func.count(ChatLink.chat_id)).where(
                        ChatLink.link_id == link_id
                    )
                )

                if count.scalar_one() == 0:
                    await session.execute(delete(LinkORM).where(LinkORM.id == link_id))

        return Link(
            id=link_id,
            url=HttpUrl(url),
            tags=tags,
            chat_id=chat_id,
        )

    @db_error_handler
    async def exist_chat(self, chat_id: int) -> bool:
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(select(exists().where(Chat.id == chat_id)))
            return bool(result.scalar())

    @db_error_handler
    async def exist_link(self, chat_id: int, url: str) -> bool:
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                select(
                    exists().where(
                        ChatLink.chat_id == chat_id,
                        LinkORM.id == ChatLink.link_id,
                        LinkORM.url == url,
                    )
                )
            )
            return bool(result.scalar())

    @db_error_handler
    async def get_chats_for_link(self, link_id: int) -> list[int]:
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                select(ChatLink.chat_id).where(ChatLink.link_id == link_id)
            )
            return [row.chat_id for row in result.all()]

    @db_error_handler
    async def update_link_timestamp(self, link_id: int, cur_date: datetime) -> None:
        async with self.AsyncSessionLocal() as session:
            await session.execute(
                update(LinkORM).where(LinkORM.id == link_id).values(updated_at=cur_date)
            )
            await session.commit()
