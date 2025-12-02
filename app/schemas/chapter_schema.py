from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChapterBase(BaseModel):
    course_id: uuid.UUID
    title: str
    description: str | None = None
    order_index: int = 0


class ChapterCreate(ChapterBase):
    pass


class ChapterUpdate(BaseModel):
    course_id: uuid.UUID | None = None
    title: str | None = None
    description: str | None = None
    order_index: int | None = None


class ChapterRead(ChapterBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


__all__ = ["ChapterBase", "ChapterCreate", "ChapterUpdate", "ChapterRead"]

