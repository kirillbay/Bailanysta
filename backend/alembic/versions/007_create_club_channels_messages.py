"""create club channels and messages

Revision ID: 007_create_club_channels_messages
Revises: 006_create_clubs
Create Date: 2026-09-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "007_create_club_channels_messages"
down_revision: Union[str, None] = "006_create_clubs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "club_channels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("club_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("club_id", "slug", name="uq_channel_club_slug"),
    )
    op.create_index(op.f("ix_club_channels_club_id"), "club_channels", ["club_id"], unique=False)
    op.create_index("ix_channels_club_position", "club_channels", ["club_id", "position"], unique=False)

    op.create_table(
        "club_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("channel_id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_edited", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["channel_id"], ["club_channels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_club_messages_author_id"), "club_messages", ["author_id"], unique=False)
    op.create_index(op.f("ix_club_messages_channel_id"), "club_messages", ["channel_id"], unique=False)
    op.create_index("ix_messages_channel_created", "club_messages", ["channel_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_messages_channel_created", table_name="club_messages")
    op.drop_index(op.f("ix_club_messages_channel_id"), table_name="club_messages")
    op.drop_index(op.f("ix_club_messages_author_id"), table_name="club_messages")
    op.drop_table("club_messages")
    op.drop_index("ix_channels_club_position", table_name="club_channels")
    op.drop_index(op.f("ix_club_channels_club_id"), table_name="club_channels")
    op.drop_table("club_channels")
