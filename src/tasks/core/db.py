from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from tasks.core.config import settings
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = create_async_engine(str(settings.DATABASE_URL), future=True, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
