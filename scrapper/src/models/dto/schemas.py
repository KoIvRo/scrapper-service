from datetime import datetime
from dataclasses import dataclass
from typing import Optional, TypeVar, Generic
from pydantic import BaseModel, HttpUrl, Field


T = TypeVar("T")


@dataclass
class PaginatedLink(Generic[T]):
    """Пагинированный ответ."""

    items: list[T]
    has_next: bool

    def __len__(self) -> int:
        return len(self.items)


@dataclass
class BaseEvent:
    """Объект хранит информацию о событий."""

    url: str  # Ссылка на событие
    updated_at: datetime
    title: str
    author: str
    preview: str

    def __str__(self) -> str:
        """Сообщение об изменениях на GitHub."""
        message = ""

        if self.url:
            message += f"Ссылка: {self.url}\n"
        if self.updated_at:
            message += f"Обновление: {self.updated_at}\n"
        if self.author:
            message += f"Автор: {self.author}\n"
        if self.title:
            message += f"Заголовок: {self.title}\n"
        if self.preview:
            message += f"Описание: {self.preview}"

        return message


@dataclass
class GitHubEvent(BaseEvent):
    """Объект хранит информацию о изменении ссылки с github."""

    pass


@dataclass
class StackOverFlowEvent(BaseEvent):
    """Объект хранит информация о изменении ссылки stackoverflow."""

    pass


@dataclass
class LinkEvent:
    """Событие связанное с ссылкой."""

    link_id: int
    url: HttpUrl  # Ссылка, которая отслеживается
    event: BaseEvent


class GlobalLink(BaseModel):
    """Глобальная хранящаяся ссылка без учета чатов, используется scheduler."""

    id: int
    url: HttpUrl
    updated_at: Optional[datetime] = None


class Link(BaseModel):
    """Модель отслеживаемой ссылки."""

    id: int
    url: HttpUrl
    chat_id: int
    tags: list[str] = Field(default_factory=list)
    updated_at: Optional[datetime] = None


class LinkUpdate(BaseModel):
    """Модель обновления ссылки согласно OpenAPI контракту."""

    id: int
    url: str
    description: str = Field(default="Обнаружно изменение")
    tgChatIds: list[int]


class ApiErrorResponse(BaseModel):
    """Ответ с ошибкой."""

    description: str
    code: Optional[str] = None
    exceptionName: Optional[str] = None
    exceptionMessage: Optional[str] = None
    stacktrace: Optional[list[str]] = None


class AddLinkRequest(BaseModel):
    """Запрос на добавление ссылки."""

    link: HttpUrl
    tags: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)


class RemoveLinkRequest(BaseModel):
    """Запрос на удаление ссылки."""

    link: HttpUrl


class LinkResponse(BaseModel):
    """Ответ с данными ссылки."""

    id: int
    url: HttpUrl
    tags: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)  # Соотвествие контракту


class ListLinksResponse(BaseModel):
    """Ответ со списком ссылок."""

    links: list[LinkResponse]
    size: int
    has_next: bool
