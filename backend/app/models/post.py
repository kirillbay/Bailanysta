"""Post + PostMedia + Hashtag models."""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, Integer, Table, Column, UniqueConstraint, Index, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid

from app.database.base import Base

# Association table post ↔ hashtag
post_hashtags = Table(
    "post_hashtags",
    Base.metadata,
    Column("post_id", Uuid, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("hashtag_id", Uuid, ForeignKey("hashtags.id", ondelete="CASCADE"), primary_key=True),
)

class Hashtag(Base):
    __tablename__ = "hashtags"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # lowercased
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    posts: Mapped[list["Post"]] = relationship(secondary=post_hashtags, back_populates="hashtags")

    def __repr__(self):
        return f"<Hashtag #{self.name}>"

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    author: Mapped["User"] = relationship(lazy="joined")
    media: Mapped[list["PostMedia"]] = relationship(back_populates="post", cascade="all, delete-orphan", order_by="PostMedia.position", lazy="selectin")
    hashtags: Mapped[list[Hashtag]] = relationship(secondary=post_hashtags, back_populates="posts", lazy="selectin")

    __table_args__ = (
        Index("ix_posts_author_created", "author_id", "created_at"),
    )

class PostMedia(Base):
    __tablename__ = "post_media"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    post: Mapped[Post] = relationship(back_populates="media")

    __table_args__ = (
        UniqueConstraint("post_id", "position", name="uq_post_media_position"),
    )
