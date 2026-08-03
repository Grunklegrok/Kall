from datetime import datetime
from typing import Any

from sqlmodel import JSON, Column, Field

from kall.models.core import TimestampMixin


class ResumeParse(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    resume_id: int = Field(index=True, foreign_key="resumedocument.id")
    parser_version: str = "rules-v1"
    status: str = "completed"
    parsed_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    warnings: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    reviewed_at: datetime | None = None


class JobRequirementAnalysis(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: int = Field(index=True, foreign_key="job.id", unique=True)
    analyzer_version: str = "rules-v1"
    required_skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    responsibilities: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    leadership_signals: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    education_requirements: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    certification_requirements: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    ats_keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    explicit_requirements: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    inferred_signals: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class Achievement(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    source_resume_id: int | None = Field(default=None, foreign_key="resumedocument.id")
    source_parse_id: int | None = Field(default=None, foreign_key="resumeparse.id")
    employer: str | None = None
    role_title: str | None = None
    achievement_text: str
    metrics: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    technologies: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    industries: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    leadership_level: str | None = None
    verification_status: str = "suggested"
    user_notes: str | None = None
