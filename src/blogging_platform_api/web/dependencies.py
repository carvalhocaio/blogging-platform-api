from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from blogging_platform_api.application.clock import Clock
from blogging_platform_api.application.posts import PostService
from blogging_platform_api.infrastructure.persistence.sqlite import (
    SQLitePostRepository,
)


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.session_factory


def get_clock(request: Request) -> Clock:
    return request.app.state.clock


async def get_session(
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> AsyncIterator[AsyncSession]:
    async with factory() as session:
        yield session


async def get_post_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    clock: Annotated[Clock, Depends(get_clock)],
) -> PostService:
    return PostService(SQLitePostRepository(session), clock)


PostServiceDep = Annotated[PostService, Depends(get_post_service)]
