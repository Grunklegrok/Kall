"""Add onboarding progress.

Revision ID: 20260802_0002
Revises: 20260802_0001
"""
import sqlalchemy as sa
from alembic import op

revision = "20260802_0002"
down_revision = "20260802_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "onboardingprogress",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("current_step", sa.String(), nullable=False),
        sa.Column("completed_steps", sa.JSON(), nullable=False),
        sa.Column("dismissed_steps", sa.JSON(), nullable=False),
        sa.Column("is_complete", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        op.f("ix_onboardingprogress_user_id"),
        "onboardingprogress",
        ["user_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_onboardingprogress_user_id"), table_name="onboardingprogress")
    op.drop_table("onboardingprogress")
