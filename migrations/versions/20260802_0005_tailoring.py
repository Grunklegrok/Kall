"""Add evidence-grounded tailoring tables.

Revision ID: 20260802_0005
Revises: 20260802_0004
"""
from alembic import op
from sqlmodel import SQLModel

import kall.models  # noqa: F401

revision = "20260802_0005"
down_revision = "20260802_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    SQLModel.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    for table in ("tailoringaudit", "tailoringchange", "tailoringproposal"):
        op.drop_table(table)
