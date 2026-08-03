"""Add social identity, TOTP, and passkey authentication.

Revision ID: 20260802_0014
Revises: 20260802_0013
"""

import sqlalchemy as sa
from alembic import op

revision = "20260802_0014"
down_revision = "20260802_0013"
branch_labels = None
depends_on = None


def timestamps() -> list[sa.Column]:
    return [sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False)]


def upgrade() -> None:
    op.add_column("usercredential", sa.Column("totp_secret_encrypted", sa.String(), nullable=True))
    op.add_column("usercredential", sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table(
        "oauthidentity",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_subject", sa.String(), nullable=False),
        sa.Column("email", sa.String()),
        *timestamps(),
        sa.UniqueConstraint("provider", "provider_subject", name="uq_oauth_provider_subject"),
    )
    op.create_table(
        "passkeycredential",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("credential_id", sa.String(), nullable=False, unique=True),
        sa.Column("public_key", sa.String(), nullable=False),
        sa.Column("sign_count", sa.Integer(), nullable=False),
        sa.Column("transports", sa.String()),
        sa.Column("last_used_at", sa.DateTime()),
        *timestamps(),
    )
    op.create_table(
        "authchallenge",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id")),
        sa.Column("purpose", sa.String(), nullable=False),
        sa.Column("challenge", sa.String(), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime()),
        *timestamps(),
    )


def downgrade() -> None:
    op.drop_table("authchallenge")
    op.drop_table("passkeycredential")
    op.drop_table("oauthidentity")
    op.drop_column("usercredential", "totp_enabled")
    op.drop_column("usercredential", "totp_secret_encrypted")
