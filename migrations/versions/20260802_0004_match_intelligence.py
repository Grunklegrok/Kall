"""Add resume match intelligence tables.

Revision ID: 20260802_0004
Revises: 20260802_0003
"""
from alembic import op
from sqlmodel import SQLModel

import kall.models  # noqa: F401

revision = "20260802_0004"
down_revision = "20260802_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in [
        "resumejobscore",
        "requirementevidence",
        "achievementjobmatch",
        "resumeselection",
    ]:
        table = SQLModel.metadata.tables[table_name]
        table.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    for table_name in [
        "resumeselection",
        "achievementjobmatch",
        "requirementevidence",
        "resumejobscore",
    ]:
        op.drop_table(table_name)
