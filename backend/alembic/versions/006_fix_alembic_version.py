"""fix alembic_version length to allow long revision ids

Revision ID: 006_fix_alembic_version
Revises: 006_create_clubs
Create Date: 2026-09-06

This migration fixes StringDataRightTruncation for revision IDs longer than 32 chars
(e.g., 007_create_club_channels_messages is 33 chars). It expands alembic_version.version_num
to VARCHAR(128) so that future revisions with descriptive names fit.
Safe for both PostgreSQL (enforces length) and SQLite (TEXT, no enforcement).

Neon production was stuck at 006 with 007 failing due to VARCHAR(32) limit. This fix
is inserted between 006 and 007, so that on next `alembic upgrade head` Neon will
first alter the column, then successfully apply 007.

For new databases, the same path is followed: 006 -> 006_fix -> 007 -> ...
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "006_fix_alembic_version"
down_revision: Union[str, None] = "006_create_clubs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch mode for SQLite compatibility, and direct ALTER for PostgreSQL
    # For PostgreSQL, alter column type to VARCHAR(128)
    # For SQLite, this is a no-op (TEXT), but we run it for consistency
    with op.batch_alter_table("alembic_version") as batch_op:
        batch_op.alter_column(
            "version_num",
            existing_type=sa.String(length=32),
            type_=sa.String(length=128),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("alembic_version") as batch_op:
        batch_op.alter_column(
            "version_num",
            existing_type=sa.String(length=128),
            type_=sa.String(length=32),
            existing_nullable=False,
        )
