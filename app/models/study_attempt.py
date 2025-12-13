from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pydantic import BaseModel

from app.database import Base


class StudyAttempt(Base):
    __tablename__ = "study_attempts"

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

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # relationships
    user: Mapped["User"] = relationship("User", back_populates="study_attempts")
    question: Mapped["Question"] = relationship("Question", back_populates="study_attempts")
    selected_option: Mapped["Option | None"] = relationship(
        "Option",
        back_populates="study_attempts",
    )


# Pydantic Schemas


class StudyAttemptBase(BaseModel):
    user_id: uuid.UUID
    question_id: uuid.UUID
    selected_option_id: uuid.UUID | None = None
    is_correct: bool


class StudyAttemptCreate(StudyAttemptBase):
    pass


class StudyAttemptRead(StudyAttemptBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True