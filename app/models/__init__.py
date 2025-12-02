from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


from . import user  # noqa: F401
from . import course  # noqa: F401
from . import chapter  # noqa: F401
from . import question  # noqa: F401
from . import option  # noqa: F401
from . import study_attempt  # noqa: F401
from . import exam_session  # noqa: F401
from . import exam_answer  # noqa: F401


__all__ = ["Base"]