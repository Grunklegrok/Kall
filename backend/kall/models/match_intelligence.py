from datetime import datetime
from typing import Any

from sqlmodel import Column, Field, JSON

from kall.models.core import TimestampMixin


class ResumeJobScore(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    job_id: int = Field(index=True, foreign_key="job.id")
    resume_id: int = Field(index=True, foreign_key="resumedocument.id")
    professional_profile_id: int = Field(index=True, foreign_key="careerprofile.id")
    scoring_version: str = "resume-match-v1"
    total_score: int
    title_score: int = 0
    industry_score: int = 0
    skills_score: int = 0
    leadership_score: int = 0
    recency_score: int = 0
    achievement_score: int = 0
    default_resume_boost: int = 0
    explanation: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    gaps: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    evidence_summary: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class RequirementEvidence(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    job_id: int = Field(index=True, foreign_key="job.id")
    resume_id: int | None = Field(default=None, foreign_key="resumedocument.id")
    requirement: str
    requirement_type: str
    evidence_status: str
    evidence_source: str | None = None
    source_record_id: int | None = None
    evidence_text: str | None = None
    confidence: int = 0


class AchievementJobMatch(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    job_id: int = Field(index=True, foreign_key="job.id")
    achievement_id: int = Field(index=True, foreign_key="achievement.id")
    scoring_version: str = "achievement-match-v1"
    score: int
    matched_requirements: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    explanation: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class ResumeSelection(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    job_id: int = Field(index=True, foreign_key="job.id")
    professional_profile_id: int = Field(index=True, foreign_key="careerprofile.id")
    recommended_resume_id: int | None = Field(default=None, foreign_key="resumedocument.id")
    selected_resume_id: int | None = Field(default=None, foreign_key="resumedocument.id")
    selection_source: str = "recommended"
    scoring_version: str = "resume-match-v1"
    selected_at: datetime | None = None
