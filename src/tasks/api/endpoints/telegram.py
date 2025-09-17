from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.api.deps import get_db
from tasks.core.config import settings
from tasks.db.crud.user import user_crud
from tasks.services.telegram import telegram_service

router = APIRouter(tags=["telegram"])


@router.post(settings.TELEGRAM_WEBHOOK_PATH)
async def telegram_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
):
    secret = request.headers.get("x-telegram-bot-api-secret-token")
    if secret != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    payload = await request.json()
    msg = payload.get("message") or payload.get("edited_message") or {}
    frm = msg.get("from") or {}
    chat = msg.get("chat") or {}
    text = msg.get("text") or ""
    chat_id = str(chat.get("id") or frm.get("id") or "")
    username = frm.get("username")
    full_name = (
        " ".join(
            [v for v in [frm.get("first_name"), frm.get("last_name")] if v]
        )
        or None
    )
    if not chat_id:
        return {"ok": True}
    await user_crud.create_or_update_telegram(
        db, chat_id, username, full_name
    )
    if text.strip().lower().startswith("/start"):
        await telegram_service.send_message(
            chat_id, "Готово. Уведомления включены."
        )
    return {"ok": True}
