from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, status

from tasks.core.config import settings
from tasks.core.constants import ACCESS_TOKEN_EXPIRE


def create_access_token(
    sub: str, expires_delta: Optional[timedelta] = None
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or ACCESS_TOKEN_EXPIRE
    )
    to_encode = {"sub": sub, "exp": expire}
    return jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG
    )


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG]
        )
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return str(sub)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
