import asyncio
import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ["APP_TITLE"] = "PyTasks Test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["JWT_SECRET"] = "test_secret_1234567890"
os.environ["JWT_ALG"] = "HS256"
os.environ["TELEGRAM_BOT_TOKEN"] = "TEST:TOKEN"
os.environ["PUBLIC_BASE_URL"] = "http://test"
os.environ["TELEGRAM_WEBHOOK_PATH"] = "/telegram/webhook"
os.environ["TELEGRAM_WEBHOOK_SECRET"] = "webhook_secret_1234567890"
os.environ["ENABLE_SCHEDULER"] = "false"

from tasks.core import db as core_db
from tasks.core.db import Base

test_engine = create_async_engine(os.environ["DATABASE_URL"], future=True)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False, class_=core_db.AsyncSession)

@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def _db_setup():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    core_db.engine = test_engine
    core_db.SessionLocal = TestSession
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(_db_setup):
    from tasks.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sent_messages(monkeypatch):
    calls = []
    from tasks.services import telegram as tg
    async def _fake_send(chat_id: str, text: str):
        calls.append((str(chat_id), str(text)))
    monkeypatch.setattr(tg.telegram_service, "send_message", _fake_send)
    return calls

@pytest.fixture
async def db_session():
    async with TestSession() as s:
        yield s

@pytest.fixture(autouse=True)
def _patch_scheduler_session(monkeypatch):
    from tasks.services import scheduler as scheduler_mod
    monkeypatch.setattr(scheduler_mod, "SessionLocal", core_db.SessionLocal, raising=True)
