from __future__ import annotations

from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.utils.config import settings

# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Import Base from models to ensure all models are registered
from app.models import Base  # noqa: E402

# Import all models to ensure they're registered with Base
from app.models import (  # noqa: E402, F401
    user,
    course_model,
    chapter_model,
    question_model,
    option,
    exam,
    exam_session,
    exam_answer,
    study_attempt,
)


async def get_db() -> AsyncGenerator[Any, None]:
    """
    Dependency that yields an async database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


__all__ = ["async_engine", "AsyncSessionLocal", "get_db", "Base"]
