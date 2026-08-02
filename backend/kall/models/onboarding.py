from sqlmodel import Column, Field, JSON

from kall.models.core import TimestampMixin


class OnboardingProgress(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id", unique=True)
    current_step: str = "identity"
    completed_steps: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    dismissed_steps: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_complete: bool = False
