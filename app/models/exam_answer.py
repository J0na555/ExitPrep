from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pydantic import BaseModel

from app.database import Base


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    selected_option_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("options.id", ondelete="SET NULL"),
        nullable=True,
    )

    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # relationships
    exam_session: Mapped["ExamSession"] = relationship(
        "ExamSession",
        back_populates="exam_answers",
    )
    question: Mapped["Question"] = relationship("Question", back_populates="exam_answers")
    selected_option: Mapped["Option | None"] = relationship(
        "Option",
        back_populates="exam_answers",
    )


# Pydantic Schemas


class ExamAnswerBase(BaseModel):
    exam_id: uuid.UUID
    question_id: uuid.UUID
    selected_option_id: uuid.UUID | None = None
    is_correct: bool


class ExamAnswerCreate(ExamAnswerBase):
    pass


class ExamAnswerRead(ExamAnswerBase):
    id: uuid.UUID

    class Config:
        orm_mode = True