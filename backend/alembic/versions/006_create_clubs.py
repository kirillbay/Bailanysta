"""create clubs

Revision ID: 006_create_clubs
Revises: 005_create_stories
Create Date: 2026-09-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "006_create_clubs"
down_revision: Union[str, None] = "005_create_stories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clubs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("cover_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_clubs_owner_id"), "clubs", ["owner_id"], unique=False)
    op.create_index(op.f("ix_clubs_slug"), "clubs", ["slug"], unique=True)

    op.create_table(
        "club_members",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("club_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("club_id", "user_id", name="uq_club_member"),
    )
    op.create_index(op.f("ix_club_members_club_id"), "club_members", ["club_id"], unique=False)
    op.create_index(op.f("ix_club_members_user_id"), "club_members", ["user_id"], unique=False)
    op.create_index("ix_club_members_club_user", "club_members", ["club_id", "user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_club_members_club_user", table_name="club_members")
    op.drop_index(op.f("ix_club_members_user_id"), table_name="club_members")
    op.drop_index(op.f("ix_club_members_club_id"), table_name="club_members")
    op.drop_table("club_members")
    op.drop_index(op.f("ix_clubs_slug"), table_name="clubs")
    op.drop_index(op.f("ix_clubs_owner_id"), table_name="clubs")
    op.drop_table("clubs")
