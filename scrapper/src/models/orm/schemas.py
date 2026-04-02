from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    BigInteger,
    TIMESTAMP,
    Integer,
    VARCHAR,
    ForeignKey,
    ForeignKeyConstraint,
    func,
    Index,
)


class Base(DeclarativeBase):
    """Базовый класс."""

    pass


class Chat(Base):
    """ORM для чатов."""

    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Link(Base):
    """ORM для ссылок"""

    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(VARCHAR(2083), unique=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    __table_args__ = (Index("idx_links_url", "url"),)


class Tag(Base):
    """ORM для тегов."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("idx_tag_name", "name"),)


class ChatLink(Base):
    """Таблица смежности чатов и линков."""

    __tablename__ = "chats_links"

    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True
    )
    link_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("links.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (
        Index("idx_chats_links_chat_id", "chat_id"),
        Index("idx_chats_links_link_id", "link_id"),
    )


class ChatLinkTag(Base):
    """Таблица принадлежности тегов к таблице смежности."""

    __tablename__ = "chats_links_tags"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    link_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["chat_id", "link_id"],
            ["chats_links.chat_id", "chats_links.link_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        Index("idx_clt_chat_link", "chat_id", "link_id"),
    )
