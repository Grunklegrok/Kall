"""Add application review workflow.

Revision ID: 20260802_0009
Revises: 20260802_0008
"""

from alembic import op
import sqlalchemy as sa

revision = "20260802_0009"
down_revision = "20260802_0008"
branch_labels = None
depends_on = None


def timestamps() -> list[sa.Column]:
    return [sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False)]


def upgrade() -> None:
    op.create_table(
        "screeningquestion",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("application.id"), nullable=False),
        sa.Column("key", sa.String(), nullable=False), sa.Column("prompt", sa.String(), nullable=False),
        sa.Column("question_type", sa.String(), nullable=False), sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False), sa.Column("category", sa.String(), nullable=False),
        sa.Column("sensitive", sa.Boolean(), nullable=False), sa.Column("source", sa.String(), nullable=False), *timestamps(),
    )
    op.create_table(
        "applicationanswer",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("application.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("screeningquestion.id"), nullable=False),
        sa.Column("value", sa.String()), sa.Column("value_json", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(), nullable=False), sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), nullable=False), sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime()), *timestamps(),
    )
    op.create_table(
        "applicationreview",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("application.id"), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False), sa.Column("documents_confirmed", sa.Boolean(), nullable=False),
        sa.Column("answers_confirmed", sa.Boolean(), nullable=False), sa.Column("sensitive_fields_confirmed", sa.Boolean(), nullable=False),
        sa.Column("attestations_confirmed", sa.Boolean(), nullable=False), sa.Column("ready_at", sa.DateTime()),
        sa.Column("approved_at", sa.DateTime()), sa.Column("readiness_issues", sa.JSON(), nullable=False), *timestamps(),
    )
    op.create_table(
        "applicationreviewaudit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("application.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("event", sa.String(), nullable=False), sa.Column("details", sa.JSON(), nullable=False), *timestamps(),
    )


def downgrade() -> None:
    for table in ["applicationreviewaudit", "applicationreview", "applicationanswer", "screeningquestion"]:
        op.drop_table(table)
