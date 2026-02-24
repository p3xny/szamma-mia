"""add reservations, tables, notifications

Revision ID: d7f2a3b9c412
Revises: c4a1e8f2d301
Create Date: 2026-02-20 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d7f2a3b9c412"
down_revision: Union[str, None] = "c4a1e8f2d301"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "restaurant_tables",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("label", sa.String(20), nullable=False),
        sa.Column("seats", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("zone", sa.String(20), nullable=False),
        sa.Column("position_x", sa.Float(), nullable=False, server_default="0"),
        sa.Column("position_y", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("table_id", sa.Integer(), sa.ForeignKey("restaurant_tables.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reservation_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.String(5), nullable=False),
        sa.Column("guest_name", sa.String(100), nullable=False),
        sa.Column("guest_phone", sa.String(20), nullable=False),
        sa.Column("guests_count", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("status", sa.String(20), nullable=False, server_default="'confirmed'"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Seed tables: 5 indoor, 6 outdoor
    # Positions are percentages within their zone container
    tables = sa.table(
        "restaurant_tables",
        sa.column("label", sa.String),
        sa.column("seats", sa.Integer),
        sa.column("zone", sa.String),
        sa.column("position_x", sa.Float),
        sa.column("position_y", sa.Float),
        sa.column("display_order", sa.Integer),
    )
    op.bulk_insert(tables, [
        # Indoor tables
        {"label": "W1", "seats": 2, "zone": "indoor", "position_x": 15, "position_y": 20, "display_order": 1},
        {"label": "W2", "seats": 4, "zone": "indoor", "position_x": 55, "position_y": 15, "display_order": 2},
        {"label": "W3", "seats": 4, "zone": "indoor", "position_x": 15, "position_y": 60, "display_order": 3},
        {"label": "W4", "seats": 2, "zone": "indoor", "position_x": 55, "position_y": 55, "display_order": 4},
        {"label": "W5", "seats": 2, "zone": "indoor", "position_x": 35, "position_y": 85, "display_order": 5},
        # Outdoor tables
        {"label": "Z1", "seats": 2, "zone": "outdoor", "position_x": 10, "position_y": 20, "display_order": 6},
        {"label": "Z2", "seats": 4, "zone": "outdoor", "position_x": 40, "position_y": 20, "display_order": 7},
        {"label": "Z3", "seats": 4, "zone": "outdoor", "position_x": 70, "position_y": 20, "display_order": 8},
        {"label": "Z4", "seats": 2, "zone": "outdoor", "position_x": 10, "position_y": 65, "display_order": 9},
        {"label": "Z5", "seats": 4, "zone": "outdoor", "position_x": 40, "position_y": 65, "display_order": 10},
        {"label": "Z6", "seats": 2, "zone": "outdoor", "position_x": 70, "position_y": 65, "display_order": 11},
    ])

    # Seed reservation_duration setting
    settings = sa.table(
        "site_settings",
        sa.column("key", sa.String),
        sa.column("value", sa.Text),
    )
    op.bulk_insert(settings, [
        {"key": "reservation_duration", "value": "2"},
    ])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("reservations")
    op.drop_table("restaurant_tables")
    op.execute("DELETE FROM site_settings WHERE key = 'reservation_duration'")
