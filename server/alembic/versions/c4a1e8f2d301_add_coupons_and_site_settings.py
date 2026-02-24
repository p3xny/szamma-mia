"""add coupons and site_settings

Revision ID: c4a1e8f2d301
Revises: b03267d5e696
Create Date: 2026-02-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4a1e8f2d301"
down_revision: Union[str, None] = "b03267d5e696"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "coupons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("discount_percent", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Seed default data
    coupons = sa.table(
        "coupons",
        sa.column("code", sa.String),
        sa.column("discount_percent", sa.Integer),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(coupons, [
        {"code": "SZAMMA10", "discount_percent": 10, "is_active": True},
    ])

    settings = sa.table(
        "site_settings",
        sa.column("key", sa.String),
        sa.column("value", sa.Text),
    )
    op.bulk_insert(settings, [
        {"key": "phone", "value": "+48 123 456 789"},
    ])


def downgrade() -> None:
    op.drop_table("site_settings")
    op.drop_table("coupons")
