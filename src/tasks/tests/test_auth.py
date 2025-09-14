import pytest
from httpx import AsyncClient
from tasks.main import app

@pytest.mark.asyncio
async def test_telegram_callback(monkeypatch):
    from tasks.core.config import settings
    settings.JWT_SECRET = "secret_secret_secret_123"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/auth/telegram/callback", json={"telegram_id": "100", "username": "u", "full_name": "F"})
        assert r.status_code == 200
        assert "access_token" in r.json()
