"""create follows

Revision ID: 004_create_follows
Revises: 003_create_social
Create Date: 2026-09-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004_create_follows"
down_revision: Union[str, None] = "003_create_social"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "follows",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("follower_id", sa.Uuid(), nullable=False),
        sa.Column("following_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["following_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("follower_id", "following_id", name="uq_follow"),
    )
    op.create_index(op.f("ix_follows_follower_id"), "follows", ["follower_id"], unique=False)
    op.create_index(op.f("ix_follows_following_id"), "follows", ["following_id"], unique=False)
    op.create_index("ix_follows_follower_following", "follows", ["follower_id", "following_id"], unique=False)
    op.create_index("ix_follows_following_follower", "follows", ["following_id", "follower_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_follows_following_follower", table_name="follows")
    op.drop_index("ix_follows_follower_following", table_name="follows")
    op.drop_index(op.f("ix_follows_following_id"), table_name="follows")
    op.drop_index(op.f("ix_follows_follower_id"), table_name="follows")
    op.drop_table("follows")
