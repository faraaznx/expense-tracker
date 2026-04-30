"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums explicitly so we control ordering and avoid double-CREATE
    op.execute("CREATE TYPE store_type AS ENUM ('physical', 'online')")
    op.execute(
        "CREATE TYPE receipt_source AS ENUM ('physical_photo', 'online_screenshot', 'manual')"
    )

    # stores
    op.create_table(
        "stores",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "type",
            postgresql.ENUM("physical", "online", name="store_type", create_type=False),
            nullable=False,
        ),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # receipts
    op.create_table(
        "receipts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("store_id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_aed", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "source",
            postgresql.ENUM(
                "physical_photo", "online_screenshot", "manual",
                name="receipt_source",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_receipts_user_id", "receipts", ["user_id"])

    # receipt_images
    op.create_table(
        "receipt_images",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("receipt_id", sa.Uuid(), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["receipt_id"], ["receipts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # line_items
    op.create_table(
        "line_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("receipt_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("normalized_name", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Numeric(8, 3), nullable=False),
        sa.Column("unit_price_aed", sa.Numeric(10, 2), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["receipt_id"], ["receipts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_line_items_normalized_name", "line_items", ["normalized_name"])

    # price_history
    op.create_table(
        "price_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("normalized_name", sa.String(500), nullable=False),
        sa.Column("store_id", sa.Uuid(), nullable=False),
        sa.Column("price_aed", sa.Numeric(10, 2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("receipt_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.ForeignKeyConstraint(["receipt_id"], ["receipts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_price_history_user_id", "price_history", ["user_id"])
    op.create_index("ix_price_history_normalized_name", "price_history", ["normalized_name"])


def downgrade() -> None:
    op.drop_table("price_history")
    op.drop_table("line_items")
    op.drop_table("receipt_images")
    op.drop_table("receipts")
    op.drop_table("stores")

    op.execute("DROP TYPE IF EXISTS receipt_source")
    op.execute("DROP TYPE IF EXISTS store_type")
