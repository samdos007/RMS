"""Initial database schema.

Revision ID: 001_initial
Revises:
Create Date: 2025-01-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=True),
    )

    # Folders table
    op.create_table(
        "folders",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("type", sa.String(20), nullable=False, default="SINGLE"),
        sa.Column("ticker_primary", sa.String(20), nullable=False, index=True),
        sa.Column("ticker_secondary", sa.String(20), nullable=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False, default=[]),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Ideas table
    op.create_table(
        "ideas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "folder_id",
            sa.String(36),
            sa.ForeignKey("folders.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("trade_type", sa.String(20), nullable=False),
        sa.Column("pair_orientation", sa.String(40), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, default="DRAFT"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("entry_price_primary", sa.Numeric(18, 6), nullable=False),
        sa.Column("entry_price_secondary", sa.Numeric(18, 6), nullable=True),
        sa.Column("position_size", sa.Numeric(18, 6), nullable=False, default=0),
        sa.Column("horizon", sa.String(20), nullable=False, default="OTHER"),
        sa.Column("thesis_md", sa.Text(), nullable=True),
        sa.Column("catalysts", sa.JSON(), nullable=False, default=[]),
        sa.Column("risks", sa.JSON(), nullable=False, default=[]),
        sa.Column("kill_criteria_md", sa.Text(), nullable=True),
        sa.Column("target_price_primary", sa.Numeric(18, 6), nullable=True),
        sa.Column("stop_level_primary", sa.Numeric(18, 6), nullable=True),
        sa.Column("target_price_secondary", sa.Numeric(18, 6), nullable=True),
        sa.Column("stop_level_secondary", sa.Numeric(18, 6), nullable=True),
        sa.Column("exit_price_primary", sa.Numeric(18, 6), nullable=True),
        sa.Column("exit_price_secondary", sa.Numeric(18, 6), nullable=True),
        sa.Column("exit_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Notes table
    op.create_table(
        "notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "idea_id",
            sa.String(36),
            sa.ForeignKey("ideas.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("note_type", sa.String(20), nullable=False, default="GENERAL"),
        sa.Column("content_md", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Attachments table
    op.create_table(
        "attachments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "folder_id",
            sa.String(36),
            sa.ForeignKey("folders.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "idea_id",
            sa.String(36),
            sa.ForeignKey("ideas.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "(folder_id IS NOT NULL AND idea_id IS NULL) OR "
            "(folder_id IS NULL AND idea_id IS NOT NULL)",
            name="attachment_belongs_to_one",
        ),
    )

    # Price snapshots table
    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "idea_id",
            sa.String(36),
            sa.ForeignKey("ideas.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("timestamp", sa.DateTime(), nullable=False, index=True),
        sa.Column("price_primary", sa.Numeric(18, 6), nullable=False),
        sa.Column("price_secondary", sa.Numeric(18, 6), nullable=True),
        sa.Column("source", sa.String(20), nullable=False, default="MANUAL"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.UniqueConstraint("idea_id", "timestamp", name="uq_idea_timestamp"),
    )

    # Earnings table
    op.create_table(
        "earnings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "folder_id",
            sa.String(36),
            sa.ForeignKey("folders.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("ticker", sa.String(20), nullable=False, index=True),
        sa.Column("fiscal_quarter", sa.String(20), nullable=False),
        sa.Column("period_end_date", sa.Date(), nullable=True),
        sa.Column("estimate_eps", sa.Numeric(18, 6), nullable=True),
        sa.Column("actual_eps", sa.Numeric(18, 6), nullable=True),
        sa.Column("estimate_rev", sa.Numeric(18, 2), nullable=True),
        sa.Column("actual_rev", sa.Numeric(18, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "folder_id", "ticker", "fiscal_quarter", name="uq_folder_ticker_quarter"
        ),
    )


def downgrade() -> None:
    op.drop_table("earnings")
    op.drop_table("price_snapshots")
    op.drop_table("attachments")
    op.drop_table("notes")
    op.drop_table("ideas")
    op.drop_table("folders")
    op.drop_table("users")
