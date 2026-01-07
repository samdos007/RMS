"""add_folder_notes

Revision ID: ff8c8b068c7d
Revises: 003_add_theme_type
Create Date: 2026-01-06 18:00:53.545797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff8c8b068c7d'
down_revision: Union[str, None] = '003_add_theme_type'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make idea_id nullable (notes can belong to either ideas OR folders)
    with op.batch_alter_table("notes", schema=None) as batch_op:
        batch_op.alter_column("idea_id", nullable=True, existing_type=sa.String(36))

        # Add folder_id column
        batch_op.add_column(sa.Column("folder_id", sa.String(36), nullable=True))

        # Add index on folder_id
        batch_op.create_index("ix_notes_folder_id", ["folder_id"])

        # Add foreign key for folder_id
        batch_op.create_foreign_key(
            "fk_notes_folder_id",
            "folders",
            ["folder_id"],
            ["id"],
            ondelete="CASCADE"
        )

    # Add check constraint: either idea_id or folder_id must be set (not both, not neither)
    # Note: SQLite doesn't support CHECK constraints via ALTER TABLE, so we rely on app-level validation


def downgrade() -> None:
    with op.batch_alter_table("notes", schema=None) as batch_op:
        # Drop foreign key and index
        batch_op.drop_constraint("fk_notes_folder_id", type_="foreignkey")
        batch_op.drop_index("ix_notes_folder_id")

        # Drop folder_id column
        batch_op.drop_column("folder_id")

        # Make idea_id non-nullable again
        batch_op.alter_column("idea_id", nullable=False, existing_type=sa.String(36))
