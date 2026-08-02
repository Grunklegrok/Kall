from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from kall.auth import get_current_user
from kall.db import get_session
from kall.models import (
    AchievementJobMatch,
    CareerProfile,
    Job,
    JobRequirementAnalysis,
    RequirementEvidence,
    ResumeDocument,
    ResumeJobScore,
    ResumeSelection,
    User,
)
from kall.services.match_intelligence import coverage_summary, rank_resumes

router = APIRouter(tags=["match-intelligence"])


class ResumeOverrideRequest(BaseModel):
    resume_id: int


@router.post("/jobs/{job_id}/intelligence/{professional_profile_id}")
def build_job_intelligence(
    job_id: int,
    professional_profile_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    job = session.get(Job, job_id)
    profile = session.get(CareerProfile, professional_profile_id)
    analysis = session.exec(select(JobRequirementAnalysis).where(JobRequirementAnalysis.job_id == job_id)).first()
    if not job or not profile or profile.user_id != current_user.id:
        raise HTTPException(404, "Job or professional profile not found")
    if not analysis:
        raise HTTPException(409, "Analyze the job requirements before ranking resumes")
    scores = rank_resumes(session, current_user.id, job, profile, analysis)
    return {"job_id": job.id, "professional_profile_id": profile.id, "scores": scores}


@router.get("/jobs/{job_id}/intelligence/{professional_profile_id}")
def get_job_intelligence(
    job_id: int,
    professional_profile_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    profile = session.get(CareerProfile, professional_profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(404, "Professional profile not found")
    scores = list(session.exec(select(ResumeJobScore).where(
        ResumeJobScore.user_id == current_user.id,
        ResumeJobScore.job_id == job_id,
        ResumeJobScore.professional_profile_id == professional_profile_id,
    ).order_by(ResumeJobScore.total_score.desc())))
    evidence = list(session.exec(select(RequirementEvidence).where(
        RequirementEvidence.user_id == current_user.id,
        RequirementEvidence.job_id == job_id,
    )))
    achievements = list(session.exec(select(AchievementJobMatch).where(
        AchievementJobMatch.user_id == current_user.id,
        AchievementJobMatch.job_id == job_id,
    ).order_by(AchievementJobMatch.score.desc())))
    selection = session.exec(select(ResumeSelection).where(
        ResumeSelection.user_id == current_user.id,
        ResumeSelection.job_id == job_id,
        ResumeSelection.professional_profile_id == professional_profile_id,
    )).first()
    return {
        "scores": scores,
        "coverage": coverage_summary(evidence),
        "evidence": evidence,
        "achievement_matches": achievements,
        "selection": selection,
    }


@router.put("/jobs/{job_id}/intelligence/{professional_profile_id}/selection", response_model=ResumeSelection)
def override_resume_selection(
    job_id: int,
    professional_profile_id: int,
    payload: ResumeOverrideRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ResumeSelection:
    profile = session.get(CareerProfile, professional_profile_id)
    resume = session.get(ResumeDocument, payload.resume_id)
    if not profile or profile.user_id != current_user.id or not resume or resume.user_id != current_user.id:
        raise HTTPException(404, "Professional profile or resume not found")
    selection = session.exec(select(ResumeSelection).where(
        ResumeSelection.user_id == current_user.id,
        ResumeSelection.job_id == job_id,
        ResumeSelection.professional_profile_id == professional_profile_id,
    )).first()
    if not selection:
        selection = ResumeSelection(
            user_id=current_user.id,
            job_id=job_id,
            professional_profile_id=professional_profile_id,
        )
    selection.selected_resume_id = resume.id
    selection.selection_source = "user_override"
    selection.selected_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(selection)
    session.commit()
    session.refresh(selection)
    return selection
