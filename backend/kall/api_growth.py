from datetime import date, datetime, timedelta
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from kall.auth import get_current_user
from kall.db import get_session
from kall.models import (
    CareerGoal,
    CareerGrowthPlan,
    GrowthMilestone,
    GrowthProgressEntry,
    GrowthResource,
    GrowthSearchQuery,
    User,
)

router = APIRouter()


class GoalCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    target_role: str = Field(min_length=2, max_length=120)
    target_industry: str | None = None
    current_level: str | None = None
    target_level: str | None = None
    target_date: date | None = None
    time_per_week_hours: int | None = Field(default=None, ge=1, le=80)
    budget_preference: str | None = None
    notes: str | None = None


class ProgressCreate(BaseModel):
    milestone_id: int | None = None
    note: str = Field(min_length=2, max_length=1000)
    evidence_url: str | None = None


def _owned_goal(session: Session, user_id: int, goal_id: int) -> CareerGoal:
    goal = session.get(CareerGoal, goal_id)
    if not goal or goal.user_id != user_id:
        raise HTTPException(404, "Career goal not found")
    return goal


def _plan_payload(session: Session, plan: CareerGrowthPlan) -> dict:
    milestones = list(session.exec(select(GrowthMilestone).where(GrowthMilestone.growth_plan_id == plan.id).order_by(GrowthMilestone.sequence)))
    resources = list(session.exec(select(GrowthResource).where(GrowthResource.growth_plan_id == plan.id)))
    searches = list(session.exec(select(GrowthSearchQuery).where(GrowthSearchQuery.growth_plan_id == plan.id)))
    progress = list(session.exec(select(GrowthProgressEntry).where(GrowthProgressEntry.growth_plan_id == plan.id).order_by(GrowthProgressEntry.occurred_at.desc())))
    return {"plan": plan, "milestones": milestones, "resources": resources, "searches": searches, "progress": progress}


@router.get("/growth")
def growth_dashboard(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> dict:
    goals = list(session.exec(select(CareerGoal).where(CareerGoal.user_id == current_user.id).order_by(CareerGoal.updated_at.desc())))
    plans = list(session.exec(select(CareerGrowthPlan).where(CareerGrowthPlan.user_id == current_user.id).order_by(CareerGrowthPlan.generated_at.desc())))
    plan_by_goal = {plan.career_goal_id: plan for plan in plans}
    return {
        "goals": [
            {
                "goal": goal,
                "plan": _plan_payload(session, plan_by_goal[goal.id]) if goal.id in plan_by_goal else None,
            }
            for goal in goals
        ]
    }


@router.post("/growth/goals", response_model=CareerGoal)
def create_goal(payload: GoalCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> CareerGoal:
    goal = CareerGoal(user_id=current_user.id, **payload.model_dump())
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.post("/growth/goals/{goal_id}/plan")
def generate_plan(goal_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> dict:
    goal = _owned_goal(session, current_user.id, goal_id)
    existing = session.exec(select(CareerGrowthPlan).where(CareerGrowthPlan.career_goal_id == goal.id)).first()
    if existing:
        return _plan_payload(session, existing)

    role = goal.target_role.strip()
    industry = (goal.target_industry or "your target industry").strip()
    hours = goal.time_per_week_hours or 5
    plan = CareerGrowthPlan(
        user_id=current_user.id,
        career_goal_id=goal.id,
        summary=f"A practical path toward {role} in {industry}, paced around roughly {hours} hours per week.",
        current_strengths=["Existing professional experience", "Transferable accomplishments", "Defined career direction"],
        skill_gaps=[f"Role-specific skills for {role}", f"Industry context for {industry}", "Portfolio or evidence aligned to the target role"],
        recommended_roles=[role, f"Associate {role}", f"Senior {role}"],
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)

    phases = [
        (1, "Foundation", "Map the role", f"Review current {role} postings and identify recurring skills, tools, and portfolio expectations.", "research", 4),
        (2, "Capability", "Close the highest-value gap", f"Complete one focused learning project that demonstrates a core {role} capability.", "education", max(8, hours * 3)),
        (3, "Evidence", "Build proof of work", f"Create or refine a portfolio artifact, case study, or achievement story relevant to {industry}.", "portfolio", max(10, hours * 4)),
        (4, "Market", "Enter the conversation", f"Connect with practitioners, request feedback, and begin targeted applications for {role} positions.", "networking", 6),
    ]
    for sequence, phase, title, description, category, estimated in phases:
        session.add(GrowthMilestone(
            user_id=current_user.id,
            growth_plan_id=plan.id,
            sequence=sequence,
            phase=phase,
            title=title,
            description=description,
            category=category,
            target_date=(datetime.utcnow() + timedelta(days=sequence * 30)).date(),
            estimated_hours=estimated,
        ))

    queries = [
        ("roles", f"{role} jobs {industry}", "Study real job requirements and vocabulary."),
        ("learning", f"best courses for {role} {industry}", "Find focused education options."),
        ("portfolio", f"{role} portfolio examples {industry}", "See credible proof-of-work examples."),
        ("community", f"{role} professional community {industry}", "Locate peers, mentors, and professional groups."),
    ]
    for category, query, rationale in queries:
        session.add(GrowthSearchQuery(
            user_id=current_user.id,
            growth_plan_id=plan.id,
            category=category,
            query=query,
            search_url=f"https://www.google.com/search?q={quote_plus(query)}",
            rationale=rationale,
        ))

    session.add(GrowthResource(
        user_id=current_user.id,
        growth_plan_id=plan.id,
        resource_type="guide",
        title=f"Build a {role} evidence portfolio",
        provider="Kall",
        url=f"https://www.google.com/search?q={quote_plus(role + ' portfolio guide')}",
        description="Use this research path to identify portfolio formats and evidence expected by hiring teams.",
        cost_type="varies",
        difficulty="intermediate",
        estimated_hours=max(6, hours * 2),
    ))
    session.commit()
    session.refresh(plan)
    return _plan_payload(session, plan)


@router.post("/growth/plans/{plan_id}/progress", response_model=GrowthProgressEntry)
def add_progress(plan_id: int, payload: ProgressCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> GrowthProgressEntry:
    plan = session.get(CareerGrowthPlan, plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(404, "Growth plan not found")
    if payload.milestone_id:
        milestone = session.get(GrowthMilestone, payload.milestone_id)
        if not milestone or milestone.growth_plan_id != plan.id:
            raise HTTPException(404, "Milestone not found")
    entry = GrowthProgressEntry(
        user_id=current_user.id,
        growth_plan_id=plan.id,
        milestone_id=payload.milestone_id,
        entry_type="note",
        note=payload.note,
        evidence_url=payload.evidence_url,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry
