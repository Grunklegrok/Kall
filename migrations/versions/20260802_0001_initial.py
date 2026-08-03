"""Initial Kall schema.

Revision ID: 20260802_0001
Revises:
"""
from alembic import op
from sqlmodel import SQLModel

import kall.models  # noqa: F401

revision = "20260802_0001"
down_revision = None
branch_labels = None
depends_on = None

# This revision originally shipped with Kall v0.3. Keep its table set frozen.
# Using all of SQLModel.metadata here makes the historical migration change every
# time a model is added, so later revisions attempt to create the same tables.
BASELINE_TABLE_NAMES = (
    "user",
    "fieldprivacy",
    "candidateprofile",
    "careerprofile",
    "resumedocument",
    "job",
    "jobmatch",
    "application",
    "reference",
    "usercredential",
    "usersession",
    "searchsource",
    "searchrun",
    "education",
    "skill",
    "certification",
    "securityclearance",
    "language",
    "awardhonor",
    "publication",
    "patent",
    "speakingengagement",
    "professionalmembership",
    "volunteerboardservice",
    "eeoprofile",
    "workauthorization",
)


def _baseline_tables():
    missing = [name for name in BASELINE_TABLE_NAMES if name not in SQLModel.metadata.tables]
    if missing:
        raise RuntimeError(f"Initial migration models are missing: {', '.join(missing)}")
    return [SQLModel.metadata.tables[name] for name in BASELINE_TABLE_NAMES]


def upgrade() -> None:
    SQLModel.metadata.create_all(bind=op.get_bind(), tables=_baseline_tables())


def downgrade() -> None:
    SQLModel.metadata.drop_all(bind=op.get_bind(), tables=_baseline_tables())
