from exceptions import ScrapperServiceError
from models.dto.schemas import ApiErrorResponse
from fastapi import APIRouter, HTTPException, Request
from dependencies.service_factory import get_service
from slowapi import Limiter
from slowapi.util import get_remote_address
from config import settings


chats = APIRouter(prefix="/tg-chat")
limiter = Limiter(get_remote_address)


@chats.post(
    "/{id}",
    responses={400: {"model": ApiErrorResponse}, 409: {"model": ApiErrorResponse}},
)
@limiter.limit(settings.rate_limit_chats_post)
async def append_chat(request: Request, id: int) -> dict:
    """Добавление чата."""

    service = get_service()
    try:
        await service.append_chat(id)

        return {"status": "ok"}
    except ScrapperServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=ApiErrorResponse(
                description=e.message,
            ).model_dump(),
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=ApiErrorResponse(description="Bad request").model_dump(),
        )


@chats.delete(
    "/{id}",
    responses={400: {"model": ApiErrorResponse}, 404: {"model": ApiErrorResponse}},
)
@limiter.limit(settings.rate_limit_links_delete)
async def delete_chat(request: Request, id: int) -> dict:
    """Удаление чата."""

    service = get_service()
    try:
        await service.delete_chat(id)

        return {"status": "ok"}
    except ScrapperServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=ApiErrorResponse(description=e.message).model_dump(),
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=ApiErrorResponse(description="Bad request").model_dump(),
        )
