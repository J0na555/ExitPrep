from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.question_model import QuestionDifficulty


class QuestionBase(BaseModel):
    chapter_id: uuid.UUID
    question_text: str
    options: dict
    correct_answer: str
    difficulty: QuestionDifficulty
    explanation: str | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    chapter_id: uuid.UUID | None = None
    question_text: str | None = None
    options: dict | None = None
    correct_answer: str | None = None
    difficulty: QuestionDifficulty | None = None
    explanation: str | None = None


class QuestionRead(QuestionBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


__all__ = ["QuestionBase", "QuestionCreate", "QuestionUpdate", "QuestionRead"]

