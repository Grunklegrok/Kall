"""Add evidence-grounded tailoring tables.

Revision ID: 20260802_0005
Revises: 20260802_0004
"""
import kall.models  # noqa: F401
from alembic import op
from sqlmodel import SQLModel

revision = "20260802_0005"
down_revision = "20260802_0004"
branch_labels = None
depends_on = None

TAILORING_TABLE_NAMES = (
    "tailoringproposal",
    "tailoringchange",
    "tailoringaudit",
)


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in TAILORING_TABLE_NAMES:
        SQLModel.metadata.tables[table_name].create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table_name in reversed(TAILORING_TABLE_NAMES):
        SQLModel.metadata.tables[table_name].drop(bind=bind, checkfirst=True)
