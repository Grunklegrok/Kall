"""Add resume intelligence tables.

Revision ID: 20260802_0003
Revises: 20260802_0002
"""
from alembic import op
from sqlmodel import SQLModel

import kall.models  # noqa: F401

revision = "20260802_0003"
down_revision = "20260802_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in ("resumeparse", "jobrequirementanalysis", "achievement"):
        SQLModel.metadata.tables[table_name].create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table_name in ("achievement", "jobrequirementanalysis", "resumeparse"):
        SQLModel.metadata.tables[table_name].drop(bind=bind, checkfirst=True)
