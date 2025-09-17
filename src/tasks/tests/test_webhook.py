import pytest
from sqlalchemy import select
from tasks.db.models.user import User
from tasks.core.config import settings

@pytest.mark.asyncio
async def test_telegram_webhook_start_creates_user(client, db_session, sent_messages):
    payload = {
        "message": {
            "text": "/start",
            "from": {"id": 11110001, "username": "tguser", "first_name": "T", "last_name": "G"},
            "chat": {"id": 11110001}
        }
    }
    r = await client.post(settings.TELEGRAM_WEBHOOK_PATH, json=payload, headers={"x-telegram-bot-api-secret-token": settings.TELEGRAM_WEBHOOK_SECRET})
    assert r.status_code == 200
    async with db_session as s:
        user = (await s.execute(select(User).where(User.telegram_id == str(11110001)))).scalar_one()
        assert user.username == "tguser"
    assert any(c[0] == str(11110001) and "Готово. Уведомления включены." in c[1] for c in sent_messages)
