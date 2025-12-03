import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import pytest
from typing import Any

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.models import Base
from app.models.user import User
from app.utils import database as dbmodule
from app.utils import dependencies as depmodule



TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def async_engine():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)

    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_init())
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture(scope="session")
def async_session_factory(async_engine):
    async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async def _create_user():
        async with async_session() as session:
            test_user = User(email="test@example.com", username="testuser", password_hash="fakehash")
            session.add(test_user)
            await session.commit()

    asyncio.run(_create_user())
    yield async_session


@pytest.fixture
async def ac(async_session_factory):
    # override get_db dependency to use the test async session
    async def override_get_db():
        async with async_session_factory() as session:
            yield session

    async def override_get_current_user(token: str = None, db: Any = None):
        async with async_session_factory() as session:
            result = await session.execute(select(User).where(User.email == "test@example.com"))
            user = result.scalar_one()
            return user

    app.dependency_overrides[dbmodule.get_db] = override_get_db
    app.dependency_overrides[depmodule.get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
