"""Add controlled submissions.

Revision ID: 20260802_0012
Revises: 20260802_0011
"""
import sqlalchemy as sa
from alembic import op

revision = "20260802_0012"
down_revision = "20260802_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("connectorcapability", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("provider", sa.String(), nullable=False, unique=True), sa.Column("supports_submission", sa.Boolean(), nullable=False), sa.Column("supports_status", sa.Boolean(), nullable=False), sa.Column("supports_files", sa.Boolean(), nullable=False), sa.Column("requires_authentication", sa.Boolean(), nullable=False), sa.Column("supported_field_types", sa.JSON(), nullable=False), sa.Column("notes", sa.String()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("applicationsubmission", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("application_id", sa.Integer(), sa.ForeignKey("application.id"), nullable=False, unique=True), sa.Column("provider", sa.String(), nullable=False), sa.Column("status", sa.String(), nullable=False), sa.Column("preview_json", sa.JSON(), nullable=False), sa.Column("preview_checksum", sa.String(), nullable=False), sa.Column("document_checksums", sa.JSON(), nullable=False), sa.Column("approval_snapshot_at", sa.DateTime()), sa.Column("confirmed_at", sa.DateTime()), sa.Column("submitted_at", sa.DateTime()), sa.Column("manual_url", sa.String()), sa.Column("failure_code", sa.String()), sa.Column("failure_detail", sa.String()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("submissionattempt", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("submission_id", sa.Integer(), sa.ForeignKey("applicationsubmission.id"), nullable=False), sa.Column("idempotency_key", sa.String(), nullable=False, unique=True), sa.Column("attempt_number", sa.Integer(), nullable=False), sa.Column("status", sa.String(), nullable=False), sa.Column("request_json", sa.JSON(), nullable=False), sa.Column("response_json", sa.JSON(), nullable=False), sa.Column("error_code", sa.String()), sa.Column("completed_at", sa.DateTime()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("submissionreceipt", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("submission_id", sa.Integer(), sa.ForeignKey("applicationsubmission.id"), nullable=False, unique=True), sa.Column("provider_receipt_id", sa.String(), nullable=False), sa.Column("confirmation_number", sa.String()), sa.Column("submitted_payload_checksum", sa.String(), nullable=False), sa.Column("receipt_json", sa.JSON(), nullable=False), sa.Column("received_at", sa.DateTime(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("submissionaudit", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("submission_id", sa.Integer(), sa.ForeignKey("applicationsubmission.id"), nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("event", sa.String(), nullable=False), sa.Column("details", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))


def downgrade() -> None:
    for table in ["submissionaudit", "submissionreceipt", "submissionattempt", "applicationsubmission", "connectorcapability"]:
        op.drop_table(table)
