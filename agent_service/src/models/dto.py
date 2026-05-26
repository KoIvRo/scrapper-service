from uuid import uuid4
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum


class Priority(str, Enum):
    """Приоритизация."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class LinkUpdate(BaseModel):
    """Модель одновления ссылки, согласно OpenAPI контракту."""

    updated_id: str = Field(default_factory=lambda: str(uuid4()))
    id: int
    author: str
    url: HttpUrl
    description: str
    tgChatIds: list[int]


class ProcessedUpdate(BaseModel):
    """Модель прошла через обработку."""

    updated_id: str = Field(default_factory=lambda: str(uuid4()))
    priority: Priority = Priority.MEDIUM
    description: str
    tgChatIds: list[int]
