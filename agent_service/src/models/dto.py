from uuid import uuid4
from pydantic import BaseModel, HttpUrl, Field


class LinkUpdate(BaseModel):
    """Модель одновления ссылки, согласно OpenAPI контракту."""

    updated_id: str = Field(default_factory=lambda: str(uuid4()))
    id: int
    url: HttpUrl
    description: str
    tgChatIds: list[int]
