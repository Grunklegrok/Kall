from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from kall.auth import get_current_user
from kall.db import get_session
from kall.models import DiscoverySchedule, NotificationPreference, Opportunity, User
from kall.services.opportunities import mark_state

router = APIRouter(tags=["opportunities"])


class ScheduleInput(BaseModel):
    professional_profile_id: int
    cadence: str = "daily"
    timezone: str = "UTC"
    hour_local: int = Field(default=8, ge=0, le=23)
    max_posting_age_days: int = Field(default=30, ge=1, le=90)


class OpportunityUpdate(BaseModel):
    state: str | None = None
    notes: str | None = None


class PreferenceInput(BaseModel):
    email_enabled: bool = True
    push_enabled: bool = False
    delivery_mode: str = "digest"
    digest_hour_local: int = Field(default=8, ge=0, le=23)
    timezone: str = "UTC"
    minimum_match_score: int = Field(default=60, ge=0, le=100)


@router.post("/discovery/schedules", response_model=DiscoverySchedule)
def create_schedule(payload: ScheduleInput, current: User = Depends(get_current_user), session: Session = Depends(get_session)):
    row = DiscoverySchedule(user_id=current.id, **payload.model_dump(exclude={"hour_local"}))
    row.run_at_local = datetime.min.replace(hour=payload.hour_local).time()
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.get("/opportunities", response_model=list[Opportunity])
def list_opportunities(state: str | None = None, current: User = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(Opportunity).where(Opportunity.user_id == current.id)
    if state:
        statement = statement.where(Opportunity.state == state)
    return list(session.exec(statement.order_by(Opportunity.match_score.desc(), Opportunity.last_seen_at.desc())))


@router.patch("/opportunities/{opportunity_id}", response_model=Opportunity)
def update_opportunity(opportunity_id: int, payload: OpportunityUpdate, current: User = Depends(get_current_user), session: Session = Depends(get_session)):
    row = session.get(Opportunity, opportunity_id)
    if not row or row.user_id != current.id:
        raise HTTPException(404, "Opportunity not found")
    if payload.state:
        try:
            mark_state(row, payload.state)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
    if payload.notes is not None:
        row.notes = payload.notes
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.put("/notification-preferences", response_model=NotificationPreference)
def set_preferences(payload: PreferenceInput, current: User = Depends(get_current_user), session: Session = Depends(get_session)):
    row = session.exec(select(NotificationPreference).where(NotificationPreference.user_id == current.id)).first()
    if not row:
        row = NotificationPreference(user_id=current.id)
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
