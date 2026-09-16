from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from blogging_platform_api.application.clock import SystemClock
from blogging_platform_api.config import Settings, get_settings
from blogging_platform_api.infrastructure.persistence.database import (
    create_engine,
    create_schema,
    create_session_factory,
)
from blogging_platform_api.web.handlers import register_handlers
from blogging_platform_api.web.routes import router


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        engine = create_engine(config.database_url, config.echo_sql)
        await create_schema(engine)
        app.state.session_factory = create_session_factory(engine)
        app.state.clock = SystemClock()
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(
        title="Blogging Platform API",
        description="Clancy's letters from Dema",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_handlers(app)
    app.include_router(router)
    return app


app = create_app()
