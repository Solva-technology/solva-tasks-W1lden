import pytest

@pytest.mark.asyncio
async def test_telegram_callback_and_me(client):
    r = await client.post("/auth/telegram/callback", json={"telegram_id": "u100", "username": "u", "full_name": "U S"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    r2 = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.json()
    assert data["telegram_id"] == "u100"
    assert data["role"] == "student"
