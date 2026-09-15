from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_serializer
from pydantic.alias_generators import to_camel

from blogging_platform_api.domain.models import Post

Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]
Content = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Category = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
Tag = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)
]


class PostPayload(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )

    title: Title
    content: Content
    category: Category
    tags: list[Tag] = Field(default_factory=list, max_length=20)


class PostResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, post: Post) -> "PostResponse":
        return cls(
            id=post.id,
            title=post.title,
            content=post.content,
            category=post.category,
            tags=list(post.tags),
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

    @field_serializer("created_at", "updated_at")
    def serializer_timestamp(self, value: datetime) -> str:
        return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    message: str
    errors: list[ErrorDetail] = Field(default_factory=list)
