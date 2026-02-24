"""add eta_minutes to orders

Revision ID: a9c4e2f1b834
Revises: f1a2b3c4d567
Create Date: 2026-02-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a9c4e2f1b834"
down_revision: Union[str, None] = "f1a2b3c4d567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("eta_minutes", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "eta_minutes")
