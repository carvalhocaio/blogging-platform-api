from collections.abc import Iterable

from blogging_platform_api.application.clock import Clock
from blogging_platform_api.domain.errors import PostNotFoundError
from blogging_platform_api.domain.models import Post, PostDraft
from blogging_platform_api.domain.repository import PostRepository


class PostService:
    def __init__(self, repository: PostRepository, clock: Clock) -> None:
        self._repository = repository
        self._clock = clock

    async def create(
        self,
        title: str,
        content: str,
        category: str,
        tags: Iterable[str],
    ) -> Post:
        draft = PostDraft.create(title, content, category, tags)
        return await self._repository.add(draft, self._clock.now())

    async def get(self, post_id: int) -> Post:
        post = await self._repository.get(post_id)
        if post is None:
            raise PostNotFoundError(post_id)
        return post

    async def search(self, term: str | None = None) -> list[Post]:
        return await self._repository.search(term)

    async def replace(
        self,
        post_id: int,
        title: str,
        content: str,
        category: str,
        tags: Iterable[str],
    ) -> Post:
        draft = PostDraft.create(title, content, category, tags)
        post = await self._repository.replace(post_id, draft, self._clock.now())
        if post is None:
            raise PostNotFoundError(post_id)
        return post

    async def delete(self, post_id: int) -> None:
        if not await self._repository.delete(post_id):
            raise PostNotFoundError(post_id)
