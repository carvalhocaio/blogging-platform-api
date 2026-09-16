from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from blogging_platform_api.config import Settings
from blogging_platform_api.domain.repository import PostRepository
from blogging_platform_api.infrastructure.persistence.database import create_schema
from blogging_platform_api.infrastructure.persistence.memory import (
    InMemoryPostRepository,
)
from blogging_platform_api.infrastructure.persistence.sqlite import (
    SQLitePostRepository,
)
from blogging_platform_api.main import create_app


class FrozenClock:
    def __init__(self, start: datetime) -> None:
        self._current = start

    def now(self) -> datetime:
        return self._current

    def advance(self, seconds: int) -> None:
        self._current += timedelta(seconds=seconds)


@pytest.fixture
def clock() -> FrozenClock:
    return FrozenClock(datetime(2018, 10, 5, 12, 0, tzinfo=UTC))


@pytest.fixture
async def memory_repository() -> AsyncIterator[PostRepository]:
    yield InMemoryPostRepository()


@pytest.fixture
async def sqlite_repository() -> AsyncIterator[PostRepository]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    await create_schema(engine)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield SQLitePostRepository(session)
    await engine.dispose()


@pytest.fixture
async def client(clock: FrozenClock) -> AsyncIterator[AsyncClient]:
    app = create_app(Settings(database_url="sqlite+aiosqlite://"))
    async with LifespanManager(app):
        app.state.clock = clock
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
