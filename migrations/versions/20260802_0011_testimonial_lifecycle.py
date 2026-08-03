"""Add testimonial lifecycle controls.

Revision ID: 20260802_0011
Revises: 20260802_0010
"""

import sqlalchemy as sa
from alembic import op

revision = "20260802_0011"
down_revision = "20260802_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("testimonialrequest", sa.Column("revoked_at", sa.DateTime(), nullable=True))
    op.add_column("testimonial", sa.Column("withdrawn_at", sa.DateTime(), nullable=True))
    op.add_column("testimonial", sa.Column("withdrawal_reason", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("testimonial", "withdrawal_reason")
    op.drop_column("testimonial", "withdrawn_at")
    op.drop_column("testimonialrequest", "revoked_at")
