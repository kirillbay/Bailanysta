"""create posts + media + hashtags

Revision ID: 002_create_posts
Revises: 001_create_users
Create Date: 2026-09-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_create_posts"
down_revision: Union[str, None] = "001_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hashtags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_hashtags_name"), "hashtags", ["name"], unique=True)

    op.create_table(
        "posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_posts_author_id"), "posts", ["author_id"], unique=False)
    op.create_index(op.f("ix_posts_created_at"), "posts", ["created_at"], unique=False)
    op.create_index("ix_posts_author_created", "posts", ["author_id", "created_at"], unique=False)

    op.create_table(
        "post_media",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("mime_type", sa.String(length=50), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("post_id", "position", name="uq_post_media_position"),
    )
    op.create_index(op.f("ix_post_media_post_id"), "post_media", ["post_id"], unique=False)

    op.create_table(
        "post_hashtags",
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("hashtag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["hashtag_id"], ["hashtags.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("post_id", "hashtag_id"),
    )


def downgrade() -> None:
    op.drop_table("post_hashtags")
    op.drop_index(op.f("ix_post_media_post_id"), table_name="post_media")
    op.drop_table("post_media")
    op.drop_index("ix_posts_author_created", table_name="posts")
    op.drop_index(op.f("ix_posts_created_at"), table_name="posts")
    op.drop_index(op.f("ix_posts_author_id"), table_name="posts")
    op.drop_table("posts")
    op.drop_index(op.f("ix_hashtags_name"), table_name="hashtags")
    op.drop_table("hashtags")
