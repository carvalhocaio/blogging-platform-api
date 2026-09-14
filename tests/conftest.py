from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest

from blogging_platform_api.domain.repository import PostRepository
from blogging_platform_api.infrastructure.persistence.memory import (
    InMemoryPostRepository,
)


class FrozenClock:
    def __init__(self, start: datetime) -> None:
        self._current = start

    def now(self) -> datetime:
        return self._current  # pyright: ignore[reportReturnType]

    def advance(self, seconds: int) -> None:
        self._current = timedelta(seconds=seconds)


@pytest.fixture
def clock() -> FrozenClock:
    return FrozenClock(datetime(2018, 10, 5, 12, 0, tzinfo=UTC))


@pytest.fixture
async def memory_repository() -> AsyncIterator[PostRepository]:
    yield InMemoryPostRepository()
