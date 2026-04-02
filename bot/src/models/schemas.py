from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class LinkUpdate(BaseModel):
    """Модель одновления ссылки, согласно OpenAPI контракту."""

    id: int
    url: HttpUrl
    description: str
    tgChatIds: list[int]


class ApiErrorResponse(BaseModel):
    """Модель ошибки, согласно OpenAPI контракту."""

    description: str
    code: Optional[str] = None
    exceptionName: Optional[str] = None
    exceptionMessage: Optional[str] = None
    stacktrace: Optional[list[str]] = None


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
