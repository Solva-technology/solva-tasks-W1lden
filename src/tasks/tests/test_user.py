import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_me(client: AsyncClient):
    r = await client.post(
        "/auth/telegram/callback",
        json={"telegram_id": "tg_me", "username": "u", "full_name": "F"},
    )
    token = r.json()["access_token"]
    me = await client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me.status_code == 200
    body = me.json()
    assert body["telegram_id"] == "tg_me"
    assert body["role"] == "student"
