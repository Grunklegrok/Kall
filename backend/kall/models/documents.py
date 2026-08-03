from datetime import datetime
from typing import Any

from sqlmodel import JSON, Column, Field

from kall.models.core import TimestampMixin


class DocumentTemplate(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True)
    name: str
    description: str
    version: str = "1"
    is_active: bool = True


class GeneratedDocument(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    proposal_id: int | None = Field(default=None, index=True, foreign_key="tailoringproposal.id")
    job_id: int | None = Field(default=None, index=True, foreign_key="job.id")
    resume_id: int | None = Field(default=None, foreign_key="resumedocument.id")
    document_type: str
    template_key: str = "standard"
    template_version: str = "1"
    status: str = "generated"
    content_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    checksum: str
    generation_version: str = "documents-v1"
    finalized_at: datetime | None = None


class DocumentArtifact(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    generated_document_id: int = Field(index=True, foreign_key="generateddocument.id")
    format: str
    file_path: str
    mime_type: str
    byte_size: int
    checksum: str


class KeywordCoverageReport(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    generated_document_id: int = Field(index=True, foreign_key="generateddocument.id", unique=True)
    required_covered: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_covered: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    unsupported: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    required_percent: int = 0
    preferred_percent: int = 0


class CoverLetterProposal(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    job_id: int = Field(index=True, foreign_key="job.id")
    tailoring_proposal_id: int = Field(index=True, foreign_key="tailoringproposal.id")
    emphasis: str = "balanced"
    tone: str = "formal"
    length: str = "standard"
    company_interest_notes: str | None = None
    status: str = "review_required"
    finalized_at: datetime | None = None


class CoverLetterChange(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(index=True, foreign_key="coverletterproposal.id")
    position: int
    original_text: str = ""
    proposed_text: str
    edited_text: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = "pending"
    reviewed_at: datetime | None = None


class DocumentGenerationAudit(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    generated_document_id: int | None = Field(default=None, foreign_key="generateddocument.id")
    event: str
    details: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
