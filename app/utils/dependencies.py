from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Any = Depends(get_db),
) -> User:
    """
    Dependency that validates JWT token and returns the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        email = payload.get("email")
        if sub is None or email is None:
            raise credentials_exception
        user_id = uuid.UUID(str(sub))
    except Exception:
        raise credentials_exception

    # Use async query
    result = await db.execute(
        select(User).where(User.id == user_id, User.email == email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


__all__ = ["get_current_user", "oauth2_scheme"]
