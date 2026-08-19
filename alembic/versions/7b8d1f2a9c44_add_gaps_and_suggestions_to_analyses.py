"""add gaps and suggestions to analyses

Revision ID: 7b8d1f2a9c44
Revises: c9f8a2e7bc4f
Create Date: 2026-08-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b8d1f2a9c44"
down_revision: Union[str, Sequence[str], None] = "c9f8a2e7bc4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("analyses", sa.Column("gaps", sa.JSON(), nullable=True))
    op.add_column("analyses", sa.Column("suggestions", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("analyses", "suggestions")
    op.drop_column("analyses", "gaps")
