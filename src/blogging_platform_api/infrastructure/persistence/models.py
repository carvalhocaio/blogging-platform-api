from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TagRow(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    slug: Mapped[str] = mapped_column(String(64), index=True)


class PostTagRow(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    position: Mapped[int]
    tag: Mapped[TagRow] = relationship(lazy="selectin")


class PostRow(Base):
    __tablename__ = "posts"
    __table_args__ = {"sqlite_autoincrement": True}  # noqa: RUF012

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str]
    category: Mapped[str] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    tag_links: Mapped[list[PostTagRow]] = relationship(
        order_by=PostTagRow.position, cascade="all, delete-orphan", lazy="selectin"
    )
