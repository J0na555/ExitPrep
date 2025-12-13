from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # relationships (kept minimal but available for other models)
    study_attempts: Mapped[List["StudyAttempt"]] = relationship(
        "StudyAttempt",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    exam_sessions: Mapped[List["ExamSession"]] = relationship(
        "ExamSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )


__all__ = ["User"]