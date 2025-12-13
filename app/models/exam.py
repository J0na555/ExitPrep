from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False) # in minutes

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    exam_sessions: Mapped[List["ExamSession"]] = relationship(
        "ExamSession",
        back_populates="exam",
        cascade="all, delete-orphan",
    )

__all__ = ["Exam"]
