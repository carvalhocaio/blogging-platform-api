from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime


def normalize_tags(tags: Iterable[str]) -> tuple[str, ...]:
    unique: dict[str, str] = {}
    for tag in tags:
        cleaned = tag.strip()
        if cleaned:
            unique.setdefault(cleaned.casefold(), cleaned)
    return tuple(unique.values())


@dataclass(frozen=True, slots=True)
class PostDraft:
    title: str
    content: str
    category: str
    tags: tuple[str, ...]

    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        category: str,
        tags: Iterable[str],
    ) -> "PostDraft":
        return cls(
            title=title.strip(),
            content=content.strip(),
            category=category.strip(),
            tags=normalize_tags(tags),
        )


@dataclass(frozen=True, slots=True)
class Post:
    id: int
    title: str
    content: str
    category: str
    tags: tuple[str, ...]
    created_at: datetime
    updated_at: datetime
