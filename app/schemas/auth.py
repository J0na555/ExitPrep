from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.schemas.user import UserResponse


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    sub: uuid.UUID
    email: EmailStr
    exp: Optional[int] = None


__all__ = ["UserLogin", "Token", "TokenData"]


