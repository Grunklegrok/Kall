from datetime import datetime

from sqlmodel import JSON, Column, Field

from kall.models.core import TimestampMixin


class SearchSource(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    provider: str
    company_name: str
    board_key: str
    enabled: bool = True


class SearchRun(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    professional_profile_id: int = Field(index=True, foreign_key="careerprofile.id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    providers_requested: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    jobs_collected: int = 0
    jobs_created: int = 0
    matches_created: int = 0
    errors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = "running"
