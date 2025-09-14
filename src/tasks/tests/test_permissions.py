import pytest
from httpx import AsyncClient
from tasks.main import app

@pytest.mark.asyncio
async def test_users_me_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/users/me")
        assert r.status_code == 401
