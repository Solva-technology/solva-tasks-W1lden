from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from tasks.core.config import settings
from tasks.core.constants import (
    DB_MAX_OVERFLOW,
    DB_POOL_RECYCLE,
    DB_POOL_SIZE,
    DB_POOL_TIMEOUT,
)


class Base(DeclarativeBase):
    pass


url = str(settings.DATABASE_URL)
backend = make_url(url).get_backend_name()

if backend == "sqlite":
    engine = create_async_engine(
        url,
        future=True,
        pool_pre_ping=True,
    )
else:
    engine = create_async_engine(
        url,
        future=True,
        pool_pre_ping=True,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=DB_POOL_RECYCLE,
    )

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
