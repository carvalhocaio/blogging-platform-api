from typing import Any

from httpx import AsyncClient

from tests.conftest import FrozenClock

LETTER: dict[str, Any] = {
    "title": "Dear Clancy",
    "content": "The bishops are watching the wall.",
    "category": "Letters",
    "tags": ["Trench", "Dema"],
}


async def create_letter(client: AsyncClient, **overrides: Any) -> dict[str, Any]:
    response = await client.post("/posts", json={**LETTER, **overrides})
    assert response.status_code == 201
    return response.json()


async def test_create_returns_201_with_full_resource(client: AsyncClient) -> None:
    body = await create_letter(client)

    assert body == {
        "id": 1,
        "title": "Dear Clancy",
        "content": "The bishops are watching the wall.",
        "category": "Letters",
        "tags": ["Trench", "Dema"],
        "createdAt": "2018-10-05T12:00:00Z",
        "updatedAt": "2018-10-05T12:00:00Z",
    }


async def test_create_rejects_blank_title(client: AsyncClient) -> None:
    response = await client.post("/posts", json={**LETTER, "title": "   "})

    assert response.status_code == 400
    assert response.json()["errors"][0]["field"] == "title"


async def test_create_rejects_unknown_field(client: AsyncClient) -> None:
    response = await client.post("/posts", json={**LETTER, "titel": "typo"})

    assert response.status_code == 400


async def test_get_returns_stored_letter(client: AsyncClient) -> None:
    created = await create_letter(client)

    response = await client.get(f"/posts/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_get_returns_404_when_missing(client: AsyncClient) -> None:
    response = await client.get("/posts/404")

    assert response.status_code == 404
    assert response.json()["message"] == "post 404 not found"


async def test_list_returns_every_letter(client: AsyncClient) -> None:
    await create_letter(client, title="Jumpsuit")
    await create_letter(client, title="Nico and the Niners")

    response = await client.get("/posts")

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == [
        "Jumpsuit",
        "Nico and the Niners",
    ]


async def test_list_filters_by_term(client: AsyncClient) -> None:
    await create_letter(client, title="Bandito", category="Trench")
    await create_letter(client, title="Smithereens", category="Scaled")

    response = await client.get("/posts", params={"term": "trench"})

    assert [item["title"] for item in response.json()] == ["Bandito"]


async def test_replace_updates_fields_and_timestamp(
    client: AsyncClient, clock: FrozenClock
) -> None:
    created = await create_letter(client)
    clock.advance(1800)

    response = await client.put(
        f"/posts/{created['id']}",
        json={**LETTER, "title": "My Updated Letter", "tags": ["Clancy"]},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["title"] == "My Updated Letter"
    assert body["tags"] == ["Clancy"]
    assert body["createdAt"] == "2018-10-05T12:00:00Z"
    assert body["updatedAt"] == "2018-10-05T12:30:00Z"


async def test_replace_returns_404_when_missing(client: AsyncClient) -> None:
    response = await client.put("/posts/404", json=LETTER)

    assert response.status_code == 404


async def test_replace_rejects_invalid_body(client: AsyncClient) -> None:
    created = await create_letter(client)

    response = await client.put(f"/posts/{created['id']}", json={"title": "Only"})

    assert response.status_code == 400


async def test_delete_removes_letter(client: AsyncClient) -> None:
    created = await create_letter(client)

    response = await client.delete(f"/posts/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert (await client.get(f"/posts/{created['id']}")).status_code == 404


async def test_delete_returns_404_when_missing(client: AsyncClient) -> None:
    response = await client.delete("/posts/404")

    assert response.status_code == 404


async def test_tags_are_deduplicated_case_insensitively(
    client: AsyncClient,
) -> None:
    body = await create_letter(client, tags=["Trench", "trench", "  Dema  "])

    assert body["tags"] == ["Trench", "Dema"]
