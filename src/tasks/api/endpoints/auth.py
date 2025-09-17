from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.api.deps import get_db
from tasks.api.schemas.auth import TelegramCallbackIn, TokenOut
from tasks.core.security import create_access_token
from tasks.db.crud.user import user_crud
from tasks.services.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram/callback", response_model=TokenOut)
async def telegram_callback(
    payload: TelegramCallbackIn, db: AsyncSession = Depends(get_db)
):
    user = await user_crud.create_or_update_telegram(
        db, payload.telegram_id, payload.username, payload.full_name
    )
    token = create_access_token(sub=user.telegram_id)
    logger.info(
        "auth",
        extra={"extra": {"user_id": user.id, "action": "login_telegram"}},
    )
    return TokenOut(access_token=token)
