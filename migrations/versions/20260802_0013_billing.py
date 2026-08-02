"""Add subscriptions, usage, and billing events.

Revision ID: 20260802_0013
Revises: 20260802_0012
"""

from alembic import op
import sqlalchemy as sa

revision = "20260802_0013"
down_revision = "20260802_0012"
branch_labels = None
depends_on = None


def timestamps() -> list[sa.Column]:
    return [sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False)]


def upgrade() -> None:
    op.create_table(
        "subscription",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, unique=True),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_customer_id", sa.String()),
        sa.Column("provider_subscription_id", sa.String()),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("plan", sa.String(), nullable=False),
        sa.Column("price_id", sa.String()),
        sa.Column("current_period_end", sa.DateTime()),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False),
        *timestamps(),
    )
    op.create_table(
        "applicationusage",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("application.id")),
        sa.Column("event", sa.String(), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        *timestamps(),
    )
    op.create_table(
        "billingevent",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_event_id", sa.String(), nullable=False, unique=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("processed_at", sa.DateTime()),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("error", sa.String()),
        *timestamps(),
    )


def downgrade() -> None:
    op.drop_table("billingevent")
    op.drop_table("applicationusage")
    op.drop_table("subscription")
