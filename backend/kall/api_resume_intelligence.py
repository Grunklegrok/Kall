from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from kall.auth import get_current_user
from kall.db import get_session
from kall.models import CareerProfile, ResumeDocument, User

router = APIRouter()


def _resume_score(resume: ResumeDocument) -> tuple[int, list[str], list[str]]:
    strengths: list[str] = []
    gaps: list[str] = []
    score = 20
    text_length = len((resume.extracted_text or "").strip())
    if text_length >= 1200:
        score += 30
        strengths.append("Substantial resume text is available for matching and tailoring.")
    elif text_length >= 400:
        score += 18
        strengths.append("Resume text was extracted successfully.")
    else:
        gaps.append("Upload a text-readable PDF or DOCX with fuller experience detail.")
    if resume.target_titles:
        score += 15
        strengths.append("Target roles are defined.")
    else:
        gaps.append("Add target titles so Kall can evaluate role alignment.")
    if resume.industries:
        score += 10
        strengths.append("Industry focus is tagged.")
    else:
        gaps.append("Add one or more target industries.")
    if resume.tags:
        score += 10
        strengths.append("Searchable resume tags are present.")
    else:
        gaps.append("Add skill or specialization tags.")
    if resume.is_default:
        score += 10
        strengths.append("This is the default resume.")
    if resume.version > 1:
        score += 5
        strengths.append("The resume has version history.")
    return min(score, 100), strengths, gaps


@router.get("/me/resume-intelligence")
def resume_intelligence(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> dict:
    resumes = list(session.exec(select(ResumeDocument).where(ResumeDocument.user_id == current_user.id).order_by(ResumeDocument.updated_at.desc())))
    profiles = list(session.exec(select(CareerProfile).where(CareerProfile.user_id == current_user.id, CareerProfile.is_active == True)))
    profile_titles = sorted({title for profile in profiles for title in profile.target_titles})
    rows = []
    for resume in resumes:
        score, strengths, gaps = _resume_score(resume)
        aligned_titles = sorted(set(resume.target_titles).intersection(profile_titles))
        rows.append({
            "id": resume.id,
            "name": resume.name,
            "version": resume.version,
            "is_default": resume.is_default,
            "tags": resume.tags,
            "industries": resume.industries,
            "target_titles": resume.target_titles,
            "updated_at": resume.updated_at,
            "readiness_score": score,
            "strengths": strengths,
            "gaps": gaps,
            "aligned_profile_titles": aligned_titles,
            "text_character_count": len(resume.extracted_text or ""),
        })
    best = max(rows, key=lambda row: row["readiness_score"], default=None)
    return {
        "summary": {
            "resume_count": len(rows),
            "profile_count": len(profiles),
            "best_resume_id": best["id"] if best else None,
            "best_score": best["readiness_score"] if best else None,
            "default_resume_id": next((row["id"] for row in rows if row["is_default"]), None),
        },
        "resumes": rows,
        "profile_titles": profile_titles,
    }
