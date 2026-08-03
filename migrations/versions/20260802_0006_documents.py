"""Add generated documents and cover letters.

Revision ID: 20260802_0006
Revises: 20260802_0005
"""

import sqlalchemy as sa
from alembic import op

revision = "20260802_0006"
down_revision = "20260802_0005"
branch_labels = None
depends_on = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "documenttemplate",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_documenttemplate_key", "documenttemplate", ["key"], unique=True)
    op.create_table(
        "generateddocument",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("proposal_id", sa.Integer(), sa.ForeignKey("tailoringproposal.id")),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("job.id")),
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumedocument.id")),
        sa.Column("document_type", sa.String(), nullable=False),
        sa.Column("template_key", sa.String(), nullable=False),
        sa.Column("template_version", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=False),
        sa.Column("generation_version", sa.String(), nullable=False),
        sa.Column("finalized_at", sa.DateTime()),
        *timestamps(),
    )
    op.create_index("ix_generateddocument_user_id", "generateddocument", ["user_id"])
    op.create_table(
        "documentartifact",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("generated_document_id", sa.Integer(), sa.ForeignKey("generateddocument.id"), nullable=False),
        sa.Column("format", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=False),
        *timestamps(),
    )
    op.create_table(
        "keywordcoveragereport",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("generated_document_id", sa.Integer(), sa.ForeignKey("generateddocument.id"), nullable=False, unique=True),
        sa.Column("required_covered", sa.JSON(), nullable=False),
        sa.Column("preferred_covered", sa.JSON(), nullable=False),
        sa.Column("unsupported", sa.JSON(), nullable=False),
        sa.Column("required_percent", sa.Integer(), nullable=False),
        sa.Column("preferred_percent", sa.Integer(), nullable=False),
        *timestamps(),
    )
    op.create_table(
        "coverletterproposal",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("job.id"), nullable=False),
        sa.Column("tailoring_proposal_id", sa.Integer(), sa.ForeignKey("tailoringproposal.id"), nullable=False),
        sa.Column("emphasis", sa.String(), nullable=False),
        sa.Column("tone", sa.String(), nullable=False),
        sa.Column("length", sa.String(), nullable=False),
        sa.Column("company_interest_notes", sa.String()),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("finalized_at", sa.DateTime()),
        *timestamps(),
    )
    op.create_index("ix_coverletterproposal_user_id", "coverletterproposal", ["user_id"])
    op.create_table(
        "coverletterchange",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proposal_id", sa.Integer(), sa.ForeignKey("coverletterproposal.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("original_text", sa.String(), nullable=False),
        sa.Column("proposed_text", sa.String(), nullable=False),
        sa.Column("edited_text", sa.String()),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime()),
        *timestamps(),
    )
    op.create_table(
        "documentgenerationaudit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("generated_document_id", sa.Integer(), sa.ForeignKey("generateddocument.id")),
        sa.Column("event", sa.String(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        *timestamps(),
    )


def downgrade() -> None:
    for table in [
        "documentgenerationaudit",
        "coverletterchange",
        "coverletterproposal",
        "keywordcoveragereport",
        "documentartifact",
        "generateddocument",
        "documenttemplate",
    ]:
        op.drop_table(table)
