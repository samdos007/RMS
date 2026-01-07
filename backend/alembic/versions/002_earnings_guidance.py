"""Add earnings expansion and guidance table.

Revision ID: 002_earnings_guidance
Revises: 001_initial
Create Date: 2026-01-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002_earnings_guidance"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to earnings table
    op.add_column("earnings", sa.Column("period_type", sa.String(20), nullable=False, server_default="QUARTERLY"))
    op.add_column("earnings", sa.Column("period", sa.String(20), nullable=True))

    # EBITDA fields
    op.add_column("earnings", sa.Column("estimate_ebitda", sa.Numeric(18, 2), nullable=True))
    op.add_column("earnings", sa.Column("actual_ebitda", sa.Numeric(18, 2), nullable=True))

    # Free Cash Flow fields
    op.add_column("earnings", sa.Column("estimate_fcf", sa.Numeric(18, 2), nullable=True))
    op.add_column("earnings", sa.Column("actual_fcf", sa.Numeric(18, 2), nullable=True))

    # User's own estimates
    op.add_column("earnings", sa.Column("my_estimate_eps", sa.Numeric(18, 6), nullable=True))
    op.add_column("earnings", sa.Column("my_estimate_rev", sa.Numeric(18, 2), nullable=True))
    op.add_column("earnings", sa.Column("my_estimate_ebitda", sa.Numeric(18, 2), nullable=True))
    op.add_column("earnings", sa.Column("my_estimate_fcf", sa.Numeric(18, 2), nullable=True))

    # Copy fiscal_quarter to period for existing data
    op.execute("UPDATE earnings SET period = fiscal_quarter WHERE period IS NULL")

    # Create guidance table
    op.create_table(
        "guidance",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "folder_id",
            sa.String(36),
            sa.ForeignKey("folders.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("ticker", sa.String(20), nullable=False, index=True),
        sa.Column("period", sa.String(20), nullable=False),  # Period the guidance is for
        sa.Column("metric", sa.String(20), nullable=False),  # REVENUE, EPS, EBITDA, FCF, OTHER
        sa.Column("guidance_period", sa.String(20), nullable=False),  # When guidance was given
        sa.Column("guidance_low", sa.Numeric(18, 6), nullable=True),
        sa.Column("guidance_high", sa.Numeric(18, 6), nullable=True),
        sa.Column("guidance_point", sa.Numeric(18, 6), nullable=True),
        sa.Column("actual_result", sa.Numeric(18, 6), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "folder_id", "ticker", "period", "metric", "guidance_period",
            name="uq_guidance_unique"
        ),
    )


def downgrade() -> None:
    op.drop_table("guidance")

    op.drop_column("earnings", "my_estimate_fcf")
    op.drop_column("earnings", "my_estimate_ebitda")
    op.drop_column("earnings", "my_estimate_rev")
    op.drop_column("earnings", "my_estimate_eps")
    op.drop_column("earnings", "actual_fcf")
    op.drop_column("earnings", "estimate_fcf")
    op.drop_column("earnings", "actual_ebitda")
    op.drop_column("earnings", "estimate_ebitda")
    op.drop_column("earnings", "period")
    op.drop_column("earnings", "period_type")
