from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from kall.auth import get_current_user
from kall.db import get_session
from kall.models import CareerGoal, CareerGrowthPlan, GrowthMilestone, GrowthProgressEntry, GrowthResource, GrowthSearchQuery, User
from kall.services.growth import build_growth_plan

router = APIRouter(prefix="/growth", tags=["career growth"])


class CareerGoalCreate(BaseModel):
    title: str
    target_role: str
    target_industry: str | None = None
    goal_type: str = "career_change"
    current_level: str | None = None
    target_level: str | None = None
    location_preference: str | None = None
    time_per_week_hours: int | None = Field(default=None, ge=1, le=80)
    budget_preference: str | None = None
    notes: str | None = None


class MilestoneUpdate(BaseModel):
    status: str


class ProgressCreate(BaseModel):
    milestone_id: int | None = None
    entry_type: str = "note"
    note: str
    evidence_url: str | None = None


def _goal(session: Session, goal_id: int, user_id: int) -> CareerGoal:
    row = session.get(CareerGoal, goal_id)
    if not row or row.user_id != user_id:
        raise HTTPException(404, "Career goal not found")
    return row


@router.post("/goals", response_model=CareerGoal)
def create_goal(payload: CareerGoalCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> CareerGoal:
    row = CareerGoal(user_id=current_user.id, **payload.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.get("/goals", response_model=list[CareerGoal])
def list_goals(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> list[CareerGoal]:
    return list(session.exec(select(CareerGoal).where(CareerGoal.user_id == current_user.id)))


@router.post("/goals/{goal_id}/plan", response_model=CareerGrowthPlan)
def generate_plan(goal_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> CareerGrowthPlan:
    return build_growth_plan(session, _goal(session, goal_id, current_user.id))


@router.get("/plans/{plan_id}")
def get_plan(plan_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> dict:
    plan = session.get(CareerGrowthPlan, plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(404, "Growth plan not found")
    milestones = list(session.exec(select(GrowthMilestone).where(GrowthMilestone.growth_plan_id == plan_id).order_by(GrowthMilestone.sequence)))
    resources = list(session.exec(select(GrowthResource).where(GrowthResource.growth_plan_id == plan_id)))
    searches = list(session.exec(select(GrowthSearchQuery).where(GrowthSearchQuery.growth_plan_id == plan_id)))
    progress = list(session.exec(select(GrowthProgressEntry).where(GrowthProgressEntry.growth_plan_id == plan_id).order_by(GrowthProgressEntry.occurred_at.desc())))
    completed = sum(1 for item in milestones if item.status == "completed")
    return {"plan": plan, "milestones": milestones, "resources": resources, "searches": searches, "progress": progress, "completion_percent": round((completed / len(milestones)) * 100) if milestones else 0}


@router.put("/milestones/{milestone_id}", response_model=GrowthMilestone)
def update_milestone(milestone_id: int, payload: MilestoneUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> GrowthMilestone:
    row = session.get(GrowthMilestone, milestone_id)
    if not row or row.user_id != current_user.id:
        raise HTTPException(404, "Milestone not found")
    row.status = payload.status
    row.completed_at = datetime.utcnow() if payload.status == "completed" else None
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.post("/plans/{plan_id}/progress", response_model=GrowthProgressEntry)
def add_progress(plan_id: int, payload: ProgressCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> GrowthProgressEntry:
    plan = session.get(CareerGrowthPlan, plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(404, "Growth plan not found")
    row = GrowthProgressEntry(user_id=current_user.id, growth_plan_id=plan_id, **payload.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
