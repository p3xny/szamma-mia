"""add scheduled time to orders

Revision ID: f1a2b3c4d567
Revises: e8b3c5d1f723
Create Date: 2026-02-20 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d567"
down_revision: Union[str, None] = "e8b3c5d1f723"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("scheduled_date", sa.Date(), nullable=True))
    op.add_column("orders", sa.Column("scheduled_time", sa.String(5), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "scheduled_time")
    op.drop_column("orders", "scheduled_date")
