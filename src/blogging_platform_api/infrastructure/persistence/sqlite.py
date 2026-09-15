from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from blogging_platform_api.domain.models import Post, PostDraft
from blogging_platform_api.infrastructure.persistence.models import (
    PostRow,
    PostTagRow,
    TagRow,
)

LIKE_ESCAPE = "\\"


def to_naive_utc(moment: datetime) -> datetime:
    return moment.astimezone(UTC).replace(tzinfo=None)


def to_aware_utc(moment: datetime) -> datetime:
    return moment.replace(tzinfo=UTC)


def to_pattern(term: str) -> str:
    escaped = (
        term.replace(LIKE_ESCAPE, LIKE_ESCAPE * 2)
        .replace("%", f"{LIKE_ESCAPE}%")
        .replace("_", f"{LIKE_ESCAPE}_")
    )
    return f"%{escaped.lower()}%"


def to_domain(row: PostRow) -> Post:
    return Post(
        id=row.id,
        title=row.title,
        content=row.content,
        category=row.category,
        tags=tuple(link.tag.name for link in row.tag_links),
        created_at=to_aware_utc(row.created_at),
        updated_at=to_aware_utc(row.updated_at),
    )


class SQLitePostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, draft: PostDraft, now: datetime) -> Post:
        timestamp = to_naive_utc(now)
        row = PostRow(
            title=draft.title,
            content=draft.content,
            category=draft.category,
            created_at=timestamp,
            updated_at=timestamp,
        )
        row.tag_links = await self._build_links(draft.tags)
        self._session.add(row)
        await self._session.commit()
        return to_domain(row)

    async def get(self, post_id: int) -> Post | None:
        row = await self._session.get(PostRow, post_id)
        return None if row is None else to_domain(row)

    async def search(self, term: str | None) -> list[Post]:
        statement = select(PostRow).order_by(PostRow.id)
        if term:
            pattern = to_pattern(term)
            statement = statement.where(
                or_(
                    func.lower(PostRow.title).like(pattern, escape=LIKE_ESCAPE),
                    func.lower(PostRow.content).like(pattern, escape=LIKE_ESCAPE),
                    func.lower(PostRow.category).like(pattern, escape=LIKE_ESCAPE),
                )
            )
        rows = await self._session.scalars(statement)
        return [to_domain(row) for row in rows]

    async def replace(
        self, post_id: int, draft: PostDraft, now: datetime
    ) -> Post | None:
        row = await self._session.get(PostRow, post_id)
        if row is None:
            return None

        row.title = draft.title
        row.content = draft.content
        row.category = draft.category
        row.updated_at = to_naive_utc(now)
        row.tag_links = await self._build_links(draft.tags)

        await self._session.commit()
        return to_domain(row)

    async def delete(self, post_id: int) -> bool:
        row = await self._session.get(PostRow, post_id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.commit()
        return True

    async def _build_links(self, names: Sequence[str]) -> list[PostTagRow]:
        if not names:
            return []

        slugs = [name.casefold() for name in names]
        existing = await self._session.scalars(
            select(TagRow).where(TagRow.slug.in_(slugs))
        )
        by_slug = {row.slug: row for row in existing}

        links: list[PostTagRow] = []
        for position, (name, slug) in enumerate(zip(names, slugs, strict=True)):
            tag = by_slug.get(slug)
            if tag is None:
                tag = TagRow(name=name, slug=slug)
                by_slug[slug] = tag
            links.append(PostTagRow(tag=tag, position=position))
        return links
