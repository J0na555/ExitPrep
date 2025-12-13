from __future__ import annotations

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.utils.config import settings

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is not set, please check your .env file.")

async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(async_database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    """
    FastAPI dependency that provides an async database session.
    """
    async with AsyncSessionLocal() as session:
        yield session

__all__ = ["engine", "AsyncSessionLocal", "Base", "get_db"]
