from dependencies.service_factory import get_service
from fastapi import APIRouter, HTTPException, Header, Request
from exceptions import ScrapperServiceError
from typing import Optional
from models.dto.schemas import (
    AddLinkRequest,
    RemoveLinkRequest,
    LinkResponse,
    ListLinksResponse,
    ApiErrorResponse,
    Link,
    PaginatedLink,
)
from slowapi import Limiter
from slowapi.util import get_remote_address
from metrics import api_requests
from config import settings

links = APIRouter(prefix="/links")
limiter = Limiter(key_func=get_remote_address)


@links.get(
    "/",
    response_model=ListLinksResponse,
    responses={400: {"model": ApiErrorResponse}, 404: {"model": ApiErrorResponse}},
)
@limiter.limit(settings.rate_limit.links_get)
async def get_links(
    request: Request,  # noqa
    page: Optional[int] = 0,
    limit: Optional[int] = 5,
    tg_chat_id: int = Header(..., alias="Tg-Chat-Id"),
):
    """Получить все ссылки."""
    api_requests.labels(source="bot").inc()

    service = get_service()

    try:
        paginated_links: PaginatedLink[Link] = await service.get_user_links_paginated(
            tg_chat_id, page, limit
        )

        links = paginated_links.items
        has_next = paginated_links.has_next

        response_links = [
            LinkResponse(
                id=link.id,
                url=link.url,
                tags=link.tags,
                filters=[],  # Не используются
            )
            for link in links
        ]

        return ListLinksResponse(
            links=response_links, size=len(response_links), has_next=has_next
        )
    except ScrapperServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=ApiErrorResponse(description=e.message).model_dump(),
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=ApiErrorResponse(
                description="Bad request",
            ).model_dump(),
        )


@links.post("")
@limiter.limit(settings.rate_limit.links_post)
async def append_link(
    request: Request,  # noqa
    add_request: AddLinkRequest,
    tg_chat_id: int = Header(..., alias="Tg-Chat-Id"),
):
    """Добавление ссылки."""
    api_requests.labels(source="bot").inc()

    service = get_service()

    try:
        link = await service.append_link(
            chat_id=tg_chat_id, url=str(add_request.link), tags=add_request.tags
        )
        return LinkResponse(id=link.id, url=link.url, tags=link.tags, filters=[])
    except ScrapperServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=ApiErrorResponse(description=e.message).model_dump(),
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=ApiErrorResponse(
                description="Bad request",
            ).model_dump(),
        )


@links.delete(
    "",
    response_model=LinkResponse,
    responses={400: {"model": ApiErrorResponse}, 404: {"model": ApiErrorResponse}},
)
@limiter.limit(settings.rate_limit.links_delete)
async def delete_link(
    request: Request,  # noqa
    remove_request: RemoveLinkRequest,
    tg_chat_id: int = Header(..., alias="Tg-Chat-Id"),
):
    """Удаление ссылки."""
    api_requests.labels(source="bot").inc()

    service = get_service()

    try:
        link = await service.delete_link(
            chat_id=tg_chat_id, url=str(remove_request.link)
        )
        return LinkResponse(id=link.id, url=link.url, tags=link.tags, filters=[])
    except ScrapperServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=ApiErrorResponse(description=e.message).model_dump(),
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=ApiErrorResponse(
                description="Bad request",
            ).model_dump(),
        )
