from datetime import date
from sqlmodel import Field
from kall.models.core import TimestampMixin


class EEOProfile(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id", unique=True)
    veteran_status_encrypted: str | None = None
    disability_status_encrypted: str | None = None
    race_ethnicity_encrypted: str | None = None
    gender_identity_encrypted: str | None = None
    decline_to_answer_defaults: bool = True
    confirmation_required: bool = True


class WorkAuthorization(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    country: str
    authorization_type: str
    citizenship_status_encrypted: str | None = None
    visa_type_encrypted: str | None = None
    authorized_from: date | None = None
    authorized_until: date | None = None
    requires_current_sponsorship: bool = False
    requires_future_sponsorship: bool = False
    confirmation_required: bool = True
