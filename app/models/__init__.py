from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


from . import user 
from . import course_model  # noqa: F401
from . import chapter_model  # noqa: F401
from . import question_model  # noqa: F401
from . import option  # noqa: F401
from . import study_attempt  # noqa: F401
from . import exam_session  # noqa: F401
from . import exam_answer  # noqa: F401


__all__ = ["Base"]