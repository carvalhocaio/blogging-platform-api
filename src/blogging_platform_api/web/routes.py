from typing import Annotated

from fastapi import APIRouter, Query, status

from blogging_platform_api.web.dependencies import PostServiceDep
from blogging_platform_api.web.schemas import (
    ErrorResponse,
    PostPayload,
    PostResponse,
)

NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}
INVALID = {status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse}}

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=INVALID,
)
async def create_post(payload: PostPayload, service: PostServiceDep) -> PostResponse:
    post = await service.create(
        payload.title, payload.content, payload.category, payload.tags
    )
    return PostResponse.from_domain(post)


@router.get("", responses=INVALID)
async def list_posts(
    service: PostServiceDep,
    term: Annotated[str | None, Query(max_length=100)] = None,
) -> list[PostResponse]:
    posts = await service.search(term)
    return [PostResponse.from_domain(post) for post in posts]


@router.get("/{post_id}", responses=NOT_FOUND)
async def get_post(post_id: int, service: PostServiceDep) -> PostResponse:
    return PostResponse.from_domain(await service.get(post_id))


@router.put("/{post_id}", responses=NOT_FOUND | INVALID)
async def replace_post(
    post_id: int, payload: PostPayload, service: PostServiceDep
) -> PostResponse:
    post = await service.replace(
        post_id, payload.title, payload.content, payload.category, payload.tags
    )
    return PostResponse.from_domain(post)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=NOT_FOUND,
)
async def delete_post(post_id: int, service: PostServiceDep) -> None:
    await service.delete(post_id)
