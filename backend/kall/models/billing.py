from datetime import datetime
from typing import Any

from sqlmodel import Column, Field, JSON

from kall.models.core import TimestampMixin


class Subscription(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id", unique=True)
    provider: str = "stripe"
    provider_customer_id: str | None = Field(default=None, index=True)
    provider_subscription_id: str | None = Field(default=None, index=True)
    status: str = "free"
    plan: str = "free"
    price_id: str | None = None
    current_period_end: datetime | None = None
    cancel_at_period_end: bool = False


class ApplicationUsage(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    application_id: int | None = Field(default=None, index=True, foreign_key="application.id")
    event: str
    units: int = 1
    metadata_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class BillingEvent(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    provider: str = "stripe"
    provider_event_id: str = Field(index=True, unique=True)
    event_type: str
    payload_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    processed_at: datetime | None = None
    status: str = "pending"
    error: str | None = None
