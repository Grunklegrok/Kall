"""Add testimonials and application references.

Revision ID: 20260802_0010
Revises: 20260802_0009
"""

from alembic import op
import sqlalchemy as sa

revision = "20260802_0010"
down_revision = "20260802_0009"
branch_labels = None
depends_on = None


def timestamps():
    return [sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False)]


def upgrade() -> None:
    op.create_table(
        "testimonialrequest",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("recipient_name", sa.String(), nullable=False),
        sa.Column("recipient_email_encrypted", sa.String(), nullable=False),
        sa.Column("relationship", sa.String(), nullable=False),
        sa.Column("request_type", sa.String(), nullable=False),
        sa.Column("personal_message", sa.String()),
        sa.Column("token_hash", sa.String(), nullable=False, unique=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("sent_at", sa.DateTime()),
        sa.Column("completed_at", sa.DateTime()),
        *timestamps(),
    )
    op.create_table(
        "testimonial",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("testimonialrequest.id")),
        sa.Column("author_name", sa.String(), nullable=False),
        sa.Column("author_title", sa.String()),
        sa.Column("author_company", sa.String()),
        sa.Column("relationship", sa.String(), nullable=False),
        sa.Column("body", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("verified_via_request", sa.Boolean(), nullable=False),
        sa.Column("include_on_profile", sa.Boolean(), nullable=False),
        sa.Column("include_in_applications", sa.Boolean(), nullable=False),
        sa.Column("permission_granted", sa.Boolean(), nullable=False),
        sa.Column("approved_at", sa.DateTime()),
        *timestamps(),
    )
    op.create_table(
        "applicationtestimonial",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("application.id"), nullable=False),
        sa.Column("testimonial_id", sa.Integer(), sa.ForeignKey("testimonial.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("included_at", sa.DateTime(), nullable=False),
        *timestamps(),
    )


def downgrade() -> None:
    op.drop_table("applicationtestimonial")
    op.drop_table("testimonial")
    op.drop_table("testimonialrequest")
