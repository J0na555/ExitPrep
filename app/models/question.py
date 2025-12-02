from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pydantic import BaseModel

from . import Base


class QuestionDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestionSource(str, enum.Enum):
    generated = "generated"
    past_paper = "past_paper"
    manual = "manual"


class Question(Base):
    __tablename__ = "questions"

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
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="SET NULL"),
        nullable=True,
    )

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        Enum(QuestionDifficulty, name="question_difficulty"),
        nullable=False,
    )

    correct_option_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("options.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    source: Mapped[QuestionSource] = mapped_column(
        Enum(QuestionSource, name="question_source"),
        nullable=False,
    )

    # relationships
    course: Mapped["Course"] = relationship("Course", back_populates="questions")
    chapter: Mapped["Chapter | None"] = relationship("Chapter", back_populates="questions")

    options: Mapped[List["Option"]] = relationship(
        "Option",
        back_populates="question",
        cascade="all, delete-orphan",
        foreign_keys="Option.question_id",
    )

    correct_option: Mapped["Option | None"] = relationship(
        "Option",
        foreign_keys=[correct_option_id],
        post_update=True,
    )

    study_attempts: Mapped[List["StudyAttempt"]] = relationship(
        "StudyAttempt",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    exam_answers: Mapped[List["ExamAnswer"]] = relationship(
        "ExamAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )


# Pydantic Schemas


class QuestionBase(BaseModel):
    course_id: uuid.UUID
    chapter_id: uuid.UUID | None = None
    question_text: str
    difficulty: QuestionDifficulty
    source: QuestionSource
    correct_option_id: uuid.UUID | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionRead(QuestionBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True