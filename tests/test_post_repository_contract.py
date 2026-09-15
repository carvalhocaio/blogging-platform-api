from datetime import UTC, datetime

import pytest

from blogging_platform_api.domain.models import PostDraft
from blogging_platform_api.domain.repository import PostRepository

NOW = datetime(2018, 10, 5, 12, 0, tzinfo=UTC)
LATER = datetime(2018, 10, 5, 12, 30, tzinfo=UTC)


def draft(
    title: str = "Dear Clancy",
    content: str = "The bishops are watching.",
    category: str = "Letters",
    tags: tuple[str, ...] = ("Trench", "Dema"),
) -> PostDraft:
    return PostDraft.create(title, content, category, tags)


@pytest.fixture(params=["memory_repository", "sqlite_repository"])
def repository(request: pytest.FixtureRequest) -> PostRepository:
    return request.getfixturevalue(request.param)


async def test_add_assigns_id_and_timestamps(repository: PostRepository) -> None:
    post = await repository.add(draft(), NOW)

    assert post.id == 1
    assert post.created_at == NOW
    assert post.updated_at == NOW
    assert post.tags == ("Trench", "Dema")


async def test_get_returns_stored_post(repository: PostRepository) -> None:
    created = await repository.add(draft(), NOW)

    assert await repository.get(created.id) == created


async def test_search_without_term_returns_all_ordered_by_id(
    repository: PostRepository,
) -> None:
    first = await repository.add(draft(title="Jumpsuit"), NOW)
    second = await repository.add(draft(title="Nico"), NOW)

    assert [post.id for post in await repository.search(None)] == [first.id, second.id]


@pytest.mark.parametrize("term", ["bandito", "BANDITO", "BaNdItO"])
async def test_search_is_case_insensitive(
    repository: PostRepository, term: str
) -> None:
    await repository.add(draft(title="Bandito"), NOW)

    assert len(await repository.search(term)) == 1


@pytest.mark.parametrize(
    "field",
    ["title", "content", "category"],
)
async def test_search_covers_title_content_and_category(
    repository: PostRepository, field: str
) -> None:
    await repository.add(draft(**{field: "Vialism"}), NOW)  # pyright: ignore[reportArgumentType]

    assert len(await repository.search("vial")) == 1


async def test_search_ignores_tags(repository: PostRepository) -> None:
    await repository.add(draft(tags=("Sahlo Folina",)), NOW)

    assert await repository.search("sahlo") == []


async def test_search_treats_wildcards_as_literal(
    repository: PostRepository,
) -> None:
    await repository.add(draft(title="Leave the city"), NOW)

    assert await repository.search("%") == []
    assert await repository.search("_") == []


async def test_replace_keeps_created_at_and_bumps_updated_at(
    repository: PostRepository,
) -> None:
    created = await repository.add(draft(), NOW)

    updated = await repository.replace(
        created.id, draft(title="Nico and the Niners"), LATER
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.title == "Nico and the Niners"
    assert updated.created_at == NOW
    assert updated.updated_at == LATER


async def test_replace_returns_none_when_missing(
    repository: PostRepository,
) -> None:
    assert await repository.replace(404, draft(), NOW) is None


async def test_delete_removes_post(repository: PostRepository) -> None:
    created = await repository.add(draft(), NOW)

    assert await repository.delete(created.id) is True
    assert await repository.get(created.id) is None


async def test_delete_returns_false_when_missing(
    repository: PostRepository,
) -> None:
    assert await repository.delete(404) is False


async def test_ids_are_not_recycled(repository: PostRepository) -> None:
    first = await repository.add(draft(), NOW)
    await repository.delete(first.id)

    second = await repository.add(draft(), NOW)

    assert second.id != first.id
