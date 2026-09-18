import asyncio
from dataclasses import dataclass

from blogging_platform_api.application.clock import SystemClock
from blogging_platform_api.application.posts import PostService
from blogging_platform_api.config import Settings, get_settings
from blogging_platform_api.infrastructure.persistence.database import (
    create_engine,
    create_schema,
    create_session_factory,
)
from blogging_platform_api.infrastructure.persistence.sqlite import (
    SQLitePostRepository,
)


@dataclass(frozen=True, slots=True)
class Letter:
    title: str
    content: str
    category: str
    tags: tuple[str, ...]


LETTERS: tuple[Letter, ...] = (
    Letter(
        title="Dear Clancy",
        content=(
            "They tell us the walls are for our protection. "
            "I have started to suspect the walls are the point."
        ),
        category="Letters",
        tags=("Dema", "Bishops"),
    ),
    Letter(
        title="Nine bishops, one city",
        content=(
            "Nicolas keeps the east tower. The other eight divide what is left. "
            "Nobody voted for any of them."
        ),
        category="Dema",
        tags=("Dema", "Nico"),
    ),
    Letter(
        title="On the practice of banditos",
        content=(
            "We leave the city at night, in yellow tape and smudged necks. "
            "Being a bandito is mostly about not being seen."
        ),
        category="Trench",
        tags=("Banditos", "Trench"),
    ),
    Letter(
        title="Sahlo Folina",
        content=(
            "A phrase for when you need to be lifted and there is no one to lift you. "
            "Say it out loud. It works more often than it should."
        ),
        category="Trench",
        tags=("Trench", "Vialism"),
    ),
    Letter(
        title="Notes on leaving",
        content=(
            "The torches move slower than they look. "
            "If you are reading this outside the wall, you already know."
        ),
        category="Letters",
        tags=("Clancy", "Dema"),
    ),
)


async def seed(settings: Settings | None = None) -> int:
    config = settings or get_settings()
    engine = create_engine(config.database_url, config.echo_sql)
    try:
        await create_schema(engine)
        factory = create_session_factory(engine)
        async with factory() as session:
            service = PostService(SQLitePostRepository(session), SystemClock())
            if await service.search():
                return 0
            for letter in LETTERS:
                await service.create(
                    letter.title, letter.content, letter.category, letter.tags
                )
        return len(LETTERS)
    finally:
        await engine.dispose()


def main() -> None:
    created = asyncio.run(seed())
    print(f"{created} letters seeded" if created else "database already seeded")


if __name__ == "__main__":
    main()
