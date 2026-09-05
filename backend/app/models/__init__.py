"""Import all models so Alembic sees them via Base.metadata."""

from app.models.user import User  # noqa: F401
from app.models.post import Post, PostMedia, Hashtag, post_hashtags  # noqa: F401
from app.models.social import PostLike, Comment, PostRepost, Bookmark  # noqa: F401

__all__ = ["User", "Post", "PostMedia", "Hashtag", "post_hashtags", "PostLike", "Comment", "PostRepost", "Bookmark"]
