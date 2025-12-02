from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pydantic import BaseModel

from . import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # relationships
    course: Mapped["Course"] = relationship("Course", back_populates="chapters")
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="chapter",
        cascade="all, delete-orphan",
    )


# Pydantic Schemas


class ChapterBase(BaseModel):
    course_id: uuid.UUID
    name: str
    description: str | None = None


class ChapterCreate(ChapterBase):
    pass


class ChapterRead(ChapterBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True