from __future__ import annotations

import uuid

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pydantic import BaseModel

from . import Base


class Option(Base):
    __tablename__ = "options"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    option_text: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # relationships
    question: Mapped["Question"] = relationship(
        "Question",
        foreign_keys=[question_id],
    )

    study_attempts: Mapped[list["StudyAttempt"]] = relationship(
        "StudyAttempt",
        back_populates="selected_option",
    )

    exam_answers: Mapped[list["ExamAnswer"]] = relationship(
        "ExamAnswer",
        back_populates="selected_option",
    )


# Pydantic Schemas


class OptionBase(BaseModel):
    question_id: uuid.UUID
    option_text: str
    is_correct: bool = False


class OptionCreate(OptionBase):
    pass


class OptionRead(OptionBase):
    id: uuid.UUID

    class Config:
        orm_mode = True