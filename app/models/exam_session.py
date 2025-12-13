from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pydantic import BaseModel

from app.models.exam_answer import ExamAnswer
from app.models.user import User

from app.database import Base


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    score_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # relationships
    user: Mapped["User"] = relationship("User", back_populates="exam_sessions")
    exam: Mapped["Exam"] = relationship("Exam", back_populates="exam_sessions")
    exam_answers: Mapped[List["ExamAnswer"]] = relationship(
        "ExamAnswer",
        back_populates="exam_session",
        cascade="all, delete-orphan",
    )


# Pydantic Schemas


class ExamSessionBase(BaseModel):
    user_id: uuid.UUID


class ExamSessionCreate(ExamSessionBase):
    pass


class ExamSessionRead(ExamSessionBase):
    id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None = None
    score_percent: float | None = None

    class Config:
        orm_mode = True