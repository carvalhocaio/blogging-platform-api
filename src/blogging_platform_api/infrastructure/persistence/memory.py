from datetime import datetime
from itertools import count

from blogging_platform_api.domain.models import Post, PostDraft


def matches(post: Post, term: str) -> bool:
    needle = term.casefold()
    haystack = (post.title, post.content, post.category)
    return any(needle in field.casefold() for field in haystack)


class InMemoryPostRepository:
    def __init__(self) -> None:
        self._posts: dict[int, Post] = {}
        self._ids = count(1)

    async def add(self, draft: PostDraft, now: datetime) -> Post:
        post = Post(
            id=next(self._ids),
            title=draft.title,
            content=draft.content,
            category=draft.category,
            tags=draft.tags,
            created_at=now,
            updated_at=now,
        )
        self._posts[post.id] = post
        return post

    async def get(self, post_id: int) -> Post | None:
        return self._posts.get(post_id)

    async def search(self, term: str | None) -> list[Post]:
        posts = sorted(self._posts.values(), key=lambda post: post.id)
        if not term:
            return posts
        return [post for post in posts if matches(post, term)]

    async def replace(
        self, post_id: int, draft: PostDraft, now: datetime
    ) -> Post | None:
        current = self._posts.get(post_id)
        if current is None:
            return None
        updated = Post(
            id=current.id,
            title=draft.title,
            content=draft.content,
            category=draft.category,
            tags=draft.tags,
            created_at=current.created_at,
            updated_at=now,
        )
        self._posts[post_id] = updated
        return updated

    async def delete(self, post_id: int) -> bool:
        return self._posts.pop(post_id, None) is not None
