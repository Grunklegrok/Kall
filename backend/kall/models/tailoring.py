from datetime import datetime
from typing import Any

from sqlmodel import JSON, Column, Field

from kall.models.core import TimestampMixin


class TailoringProposal(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    job_id: int = Field(index=True, foreign_key="job.id")
    resume_id: int = Field(index=True, foreign_key="resumedocument.id")
    professional_profile_id: int = Field(index=True, foreign_key="careerprofile.id")
    provider: str = "deterministic"
    provider_version: str = "tailoring-v1"
    status: str = "review_required"
    unsupported_requirements: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    finalized_at: datetime | None = None


class TailoringChange(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(index=True, foreign_key="tailoringproposal.id")
    section: str
    original_text: str
    proposed_text: str
    edited_text: str | None = None
    reason: str
    evidence: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    immutable_tokens: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    confidence: float = 1.0
    status: str = "pending"
    reviewed_at: datetime | None = None


class TailoringAudit(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(index=True, foreign_key="tailoringproposal.id")
    event: str
    details: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
