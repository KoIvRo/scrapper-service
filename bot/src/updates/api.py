from fastapi import APIRouter, HTTPException
from bot_instance import get_bot
from models.schemas import LinkUpdate, ApiErrorResponse
from .update_handler import handle_update


update = APIRouter(prefix="/updates")


@update.post(
    "",
    responses={
        200: {"description": "Обновление обработано"},
        400: {"model": ApiErrorResponse},
    },
)
async def get_updates(update: LinkUpdate) -> dict:
    """Полчучение уведомления."""

    try:
        await handle_update(update)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=ApiErrorResponse(
                description=str(e),
                exceptionName=type(e).__name__,
                exceptionMessage=str(e),
            ).model_dump(),
        )
