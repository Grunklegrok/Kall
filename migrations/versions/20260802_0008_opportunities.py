"""Add scheduled discovery and opportunity inbox.

Revision ID: 20260802_0008
Revises: 20260802_0007
"""
import sqlalchemy as sa
from alembic import op

revision = "20260802_0008"
down_revision = "20260802_0007"
branch_labels = None
depends_on = None

GROWTH_GOAL_TABLE = "careergoal"


def stamps():
    return [sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False)]


def upgrade() -> None:
    op.create_table("discoveryschedule", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("professional_profile_id", sa.Integer(), sa.ForeignKey("careerprofile.id"), nullable=False), sa.Column("cadence", sa.String(), nullable=False), sa.Column("timezone", sa.String(), nullable=False), sa.Column("run_at_local", sa.Time(), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False), sa.Column("max_posting_age_days", sa.Integer(), nullable=False), sa.Column("next_run_at", sa.DateTime()), sa.Column("last_run_at", sa.DateTime()), sa.Column("running_since", sa.DateTime()), *stamps())
    op.create_table("opportunity", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("professional_profile_id", sa.Integer(), sa.ForeignKey("careerprofile.id"), nullable=False), sa.Column("job_id", sa.Integer(), sa.ForeignKey("job.id"), nullable=False), sa.Column("canonical_key", sa.String(), nullable=False), sa.Column("state", sa.String(), nullable=False), sa.Column("match_score", sa.Integer(), nullable=False), sa.Column("selected_resume_id", sa.Integer(), sa.ForeignKey("resumedocument.id")), sa.Column("notes", sa.String()), sa.Column("source_records", sa.JSON(), nullable=False), sa.Column("material_fingerprint", sa.String(), nullable=False), sa.Column("first_seen_at", sa.DateTime(), nullable=False), sa.Column("last_seen_at", sa.DateTime(), nullable=False), sa.Column("dismissed_fingerprint", sa.String()), *stamps())
    op.create_index("ix_opportunity_user_id", "opportunity", ["user_id"])
    op.create_index("ix_opportunity_canonical_key", "opportunity", ["canonical_key"])
    op.create_table("notificationpreference", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, unique=True), sa.Column("email_enabled", sa.Boolean(), nullable=False), sa.Column("push_enabled", sa.Boolean(), nullable=False), sa.Column("delivery_mode", sa.String(), nullable=False), sa.Column("digest_hour_local", sa.Integer(), nullable=False), sa.Column("timezone", sa.String(), nullable=False), sa.Column("quiet_hours_start", sa.Time()), sa.Column("quiet_hours_end", sa.Time()), sa.Column("minimum_match_score", sa.Integer(), nullable=False), *stamps())
    op.create_table("deviceregistration", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("platform", sa.String(), nullable=False), sa.Column("token_hash", sa.String(), nullable=False, unique=True), sa.Column("encrypted_token", sa.String(), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False), sa.Column("last_seen_at", sa.DateTime(), nullable=False), *stamps())
    op.create_table("notificationdelivery", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity.id")), sa.Column("channel", sa.String(), nullable=False), sa.Column("kind", sa.String(), nullable=False), sa.Column("status", sa.String(), nullable=False), sa.Column("dedupe_key", sa.String(), nullable=False), sa.Column("payload", sa.JSON(), nullable=False), sa.Column("attempts", sa.Integer(), nullable=False), sa.Column("last_error", sa.String()), sa.Column("delivered_at", sa.DateTime()), sa.Column("next_attempt_at", sa.DateTime()), *stamps())
    op.create_table("growthmarketsignal", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("growth_goal_id", sa.Integer(), sa.ForeignKey(f"{GROWTH_GOAL_TABLE}.id"), nullable=False), sa.Column("observed_jobs", sa.Integer(), nullable=False), sa.Column("recurring_skills", sa.JSON(), nullable=False), sa.Column("recurring_requirements", sa.JSON(), nullable=False), sa.Column("portfolio_signals", sa.JSON(), nullable=False), sa.Column("generated_at", sa.DateTime(), nullable=False), *stamps())


def downgrade() -> None:
    for table in ["growthmarketsignal", "notificationdelivery", "deviceregistration", "notificationpreference", "opportunity", "discoveryschedule"]:
        op.drop_table(table)
