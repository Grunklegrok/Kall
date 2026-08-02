"""Add career growth and education planning.

Revision ID: 20260802_0007
Revises: 20260802_0006
"""

from alembic import op
import sqlalchemy as sa

revision = "20260802_0007"
down_revision = "20260802_0006"
branch_labels = None
depends_on = None


def timestamps() -> list[sa.Column]:
    return [sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False)]


def upgrade() -> None:
    op.create_table("careergoal", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("title", sa.String(), nullable=False), sa.Column("target_role", sa.String(), nullable=False), sa.Column("target_industry", sa.String()), sa.Column("goal_type", sa.String(), nullable=False), sa.Column("current_level", sa.String()), sa.Column("target_level", sa.String()), sa.Column("target_date", sa.Date()), sa.Column("location_preference", sa.String()), sa.Column("time_per_week_hours", sa.Integer()), sa.Column("budget_preference", sa.String()), sa.Column("notes", sa.String()), sa.Column("status", sa.String(), nullable=False), *timestamps())
    op.create_index("ix_careergoal_user_id", "careergoal", ["user_id"])
    op.create_index("ix_careergoal_target_role", "careergoal", ["target_role"])
    op.create_table("careergrowthplan", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("career_goal_id", sa.Integer(), sa.ForeignKey("careergoal.id"), nullable=False), sa.Column("provider", sa.String(), nullable=False), sa.Column("provider_version", sa.String(), nullable=False), sa.Column("status", sa.String(), nullable=False), sa.Column("summary", sa.String(), nullable=False), sa.Column("current_strengths", sa.JSON(), nullable=False), sa.Column("skill_gaps", sa.JSON(), nullable=False), sa.Column("recommended_roles", sa.JSON(), nullable=False), sa.Column("generated_at", sa.DateTime(), nullable=False), *timestamps())
    op.create_index("ix_careergrowthplan_user_id", "careergrowthplan", ["user_id"])
    op.create_table("growthmilestone", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("growth_plan_id", sa.Integer(), sa.ForeignKey("careergrowthplan.id"), nullable=False), sa.Column("sequence", sa.Integer(), nullable=False), sa.Column("phase", sa.String(), nullable=False), sa.Column("title", sa.String(), nullable=False), sa.Column("description", sa.String(), nullable=False), sa.Column("category", sa.String(), nullable=False), sa.Column("target_date", sa.Date()), sa.Column("estimated_hours", sa.Integer()), sa.Column("status", sa.String(), nullable=False), sa.Column("completed_at", sa.DateTime()), *timestamps())
    op.create_table("growthresource", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("growth_plan_id", sa.Integer(), sa.ForeignKey("careergrowthplan.id"), nullable=False), sa.Column("milestone_id", sa.Integer(), sa.ForeignKey("growthmilestone.id")), sa.Column("resource_type", sa.String(), nullable=False), sa.Column("title", sa.String(), nullable=False), sa.Column("provider", sa.String()), sa.Column("url", sa.String(), nullable=False), sa.Column("description", sa.String()), sa.Column("cost_type", sa.String()), sa.Column("difficulty", sa.String()), sa.Column("estimated_hours", sa.Integer()), sa.Column("saved", sa.Boolean(), nullable=False), sa.Column("completed", sa.Boolean(), nullable=False), sa.Column("metadata_json", sa.JSON(), nullable=False), *timestamps())
    op.create_table("growthsearchquery", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("growth_plan_id", sa.Integer(), sa.ForeignKey("careergrowthplan.id"), nullable=False), sa.Column("category", sa.String(), nullable=False), sa.Column("query", sa.String(), nullable=False), sa.Column("search_url", sa.String(), nullable=False), sa.Column("rationale", sa.String(), nullable=False), sa.Column("last_run_at", sa.DateTime()), *timestamps())
    op.create_table("growthprogressentry", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False), sa.Column("growth_plan_id", sa.Integer(), sa.ForeignKey("careergrowthplan.id"), nullable=False), sa.Column("milestone_id", sa.Integer(), sa.ForeignKey("growthmilestone.id")), sa.Column("entry_type", sa.String(), nullable=False), sa.Column("note", sa.String(), nullable=False), sa.Column("evidence_url", sa.String()), sa.Column("occurred_at", sa.DateTime(), nullable=False), *timestamps())


def downgrade() -> None:
    for table in ["growthprogressentry", "growthsearchquery", "growthresource", "growthmilestone", "careergrowthplan", "careergoal"]:
        op.drop_table(table)
