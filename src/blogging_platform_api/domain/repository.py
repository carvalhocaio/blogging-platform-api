from datetime import datetime
from typing import Protocol

from blogging_platform_api.domain.models import Post, PostDraft


class PostRepository(Protocol):
    async def add(self, draft: PostDraft, now: datetime) -> Post: ...

    async def get(self, post_id: int) -> Post | None: ...

    async def search(self, term: str | None) -> list[Post]: ...

    async def replace(
        self, post_id: int, draft: PostDraft, now: datetime
    ) -> Post | None: ...

    async def delete(self, post_id: int) -> bool: ...
