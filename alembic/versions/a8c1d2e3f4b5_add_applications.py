"""add applications table

Revision ID: a8c1d2e3f4b5
Revises: 7b8d1f2a9c44
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a8c1d2e3f4b5"
down_revision: Union[str, Sequence[str], None] = "7b8d1f2a9c44"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("analysis_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("resume_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("jd_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("job_url", sa.String(length=1000), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("applied_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"]),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"]),
        sa.ForeignKeyConstraint(["jd_id"], ["job_descriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("analysis_id", name="uq_applications_analysis_id"),
    )


def downgrade() -> None:
    op.drop_table("applications")
