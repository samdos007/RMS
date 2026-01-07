"""Add THEME folder type support.

Revision ID: 003_add_theme_type
Revises: 002_earnings_guidance
Create Date: 2026-01-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_add_theme_type"
down_revision: Union[str, None] = "002_earnings_guidance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN to change nullability
    # We need to use batch operations to recreate the table
    with op.batch_alter_table("folders", schema=None) as batch_op:
        # Make ticker_primary nullable (for THEME folders)
        batch_op.alter_column("ticker_primary", nullable=True, existing_type=sa.String(20))

        # Add theme-specific fields
        batch_op.add_column(sa.Column("theme_name", sa.String(100), nullable=True))
        batch_op.add_column(sa.Column("theme_date", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("theme_thesis", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("theme_tickers", sa.JSON(), nullable=False, server_default='[]'))

        # Add theme association field (for SINGLE/PAIR folders to link to themes)
        batch_op.add_column(sa.Column("theme_ids", sa.JSON(), nullable=False, server_default='[]'))

        # Create index for theme_name
        batch_op.create_index("ix_folders_theme_name", ["theme_name"])

    # Note: SQLite doesn't support partial indexes for uniqueness
    # We handle theme_name uniqueness at the application level


def downgrade() -> None:
    with op.batch_alter_table("folders", schema=None) as batch_op:
        # Drop index and columns
        batch_op.drop_index("ix_folders_theme_name")
        batch_op.drop_column("theme_ids")
        batch_op.drop_column("theme_tickers")
        batch_op.drop_column("theme_thesis")
        batch_op.drop_column("theme_date")
        batch_op.drop_column("theme_name")

        # Make ticker_primary non-nullable again
        batch_op.alter_column("ticker_primary", nullable=False, existing_type=sa.String(20))
