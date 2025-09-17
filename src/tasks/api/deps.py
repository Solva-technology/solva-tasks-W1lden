from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.core.db import SessionLocal
from tasks.core.enums import UserRole
from tasks.core.security import decode_access_token
from tasks.db.crud.user import user_crud


async def get_db():
    async with SessionLocal() as session:
        yield session


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = authorization.split(" ", 1)[1]
    sub = decode_access_token(token)
    user = await user_crud.get_by_telegram(db, sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


def require_roles(*roles: UserRole):
    async def checker(current=Depends(get_current_user)):
        if current.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return current

    return checker
