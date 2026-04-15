"""add subtopic columns to user_progress

Revision ID: 1b2a9cf76d51
Revises: 509bedc7ef2a
Create Date: 2026-04-15 08:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b2a9cf76d51"
down_revision: Union[str, Sequence[str], None] = "509bedc7ef2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_progress", sa.Column("subtopic_index", sa.Integer(), nullable=True))
    op.add_column("user_progress", sa.Column("subtopic_name", sa.String(length=255), nullable=True))

    # Backfill legacy rows where topic was stored as "<unit>:<index>".
    op.execute(
        """
        UPDATE user_progress
        SET
            subtopic_index = split_part(topic, ':', 2)::int,
            topic = split_part(topic, ':', 1)
        WHERE topic ~ '^[^:]+:[0-9]+$'
          AND subtopic_index IS NULL;
        """
    )

    op.create_index(
        "ix_user_progress_user_language_unit_subtopic",
        "user_progress",
        ["user_id", "language", "topic", "subtopic_index"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_progress_user_language_unit_subtopic", table_name="user_progress")
    op.drop_column("user_progress", "subtopic_name")
    op.drop_column("user_progress", "subtopic_index")
