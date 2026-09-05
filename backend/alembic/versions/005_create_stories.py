"""create stories

Revision ID: 005_create_stories
Revises: 004_create_follows
Create Date: 2026-09-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005_create_stories"
down_revision: Union[str, None] = "004_create_follows"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("media_url", sa.String(length=512), nullable=True),
        sa.Column("media_type", sa.String(length=20), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stories_author_id"), "stories", ["author_id"], unique=False)
    op.create_index(op.f("ix_stories_expires_at"), "stories", ["expires_at"], unique=False)
    op.create_index("ix_stories_author_expires", "stories", ["author_id", "expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_stories_author_expires", table_name="stories")
    op.drop_index(op.f("ix_stories_expires_at"), table_name="stories")
    op.drop_index(op.f("ix_stories_author_id"), table_name="stories")
    op.drop_table("stories")
