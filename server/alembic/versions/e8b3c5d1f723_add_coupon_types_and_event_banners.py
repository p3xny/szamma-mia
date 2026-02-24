"""add coupon types and event banners

Revision ID: e8b3c5d1f723
Revises: d7f2a3b9c412
Create Date: 2026-02-20 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e8b3c5d1f723"
down_revision: Union[str, None] = "d7f2a3b9c412"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Coupon: add discount_type and discount_amount columns
    op.add_column("coupons", sa.Column(
        "discount_type", sa.String(10), nullable=False, server_default="percent",
    ))
    op.add_column("coupons", sa.Column(
        "discount_amount", sa.Numeric(), nullable=True,
    ))

    # Event banners table
    op.create_table(
        "event_banners",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("subtitle", sa.String(300), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("link_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("event_banners")
    op.drop_column("coupons", "discount_amount")
    op.drop_column("coupons", "discount_type")
