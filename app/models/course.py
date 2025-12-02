from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pydantic import BaseModel

from . import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # relationships
    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="course",
        cascade="all, delete-orphan",
    )


# Pydantic Schemas


class CourseBase(BaseModel):
    name: str
    description: str | None = None


class CourseCreate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True