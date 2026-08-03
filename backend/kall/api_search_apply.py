from datetime import datetime
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlmodel import Session, select

from kall.auth import get_current_user
from kall.db import get_session
from kall.models import Application, CareerProfile, Job, ResumeDocument, User
from kall.models.enums import ApplicationStatus
from kall.schemas import ExternalJobImportRequest, PrepareApplicationRequest
from kall.services.applications import prepare_application

router = APIRouter()


class TrackExternalApplicationRequest(BaseModel):
    url: HttpUrl
    title: str
    snippet: str | None = None
    source: str = "google_cse"
    professional_profile_id: int


def _company_from_url(url: str) -> str:
    host = (urlparse(url).hostname or "Unknown company").lower()
    host = host.removeprefix("www.")
    labels = host.split(".")
    if len(labels) >= 2:
        return labels[-2].replace("-", " ").title()
    return host.replace("-", " ").title()


def _import_job(session: Session, url: str, title: str, snippet: str | None, source: str) -> Job:
    existing = session.exec(select(Job).where(Job.url == url)).first()
    if existing:
        return existing
    row = Job(
        source=source,
        external_id=url,
        company=_company_from_url(url),
        title=title,
        description=snippet or "Imported from Google Programmable Search. Open the original posting for complete requirements.",
        url=url,
        metadata_json={"imported_from": "google_programmable_search"},
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.post("/jobs/import-search-result", response_model=Job)
def import_search_result(
    payload: ExternalJobImportRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Job:
    del current_user
    row = _import_job(session, str(payload.url), payload.title, payload.snippet, payload.source)
    if payload.company and row.company != payload.company:
        row.company = payload.company
        session.add(row)
        session.commit()
        session.refresh(row)
    return row


@router.post("/applications/track-external", response_model=Application)
def track_external_application(
    payload: TrackExternalApplicationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Application:
    profile = session.get(CareerProfile, payload.professional_profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(404, "Professional profile not found")

    job = _import_job(session, str(payload.url), payload.title, payload.snippet, payload.source)
    existing = session.exec(
        select(Application).where(Application.user_id == current_user.id, Application.job_id == job.id)
    ).first()
    if existing:
        existing.status = ApplicationStatus.SUBMITTED
        existing.submitted_at = existing.submitted_at or datetime.utcnow()
        existing.prepared_payload = {**existing.prepared_payload, "tracked_externally": True}
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    row = Application(
        user_id=current_user.id,
        job_id=job.id,
        career_profile_id=profile.id,
        status=ApplicationStatus.SUBMITTED,
        submitted_at=datetime.utcnow(),
        prepared_payload={"tracked_externally": True, "source": payload.source},
    )
    session.add(row)
    current_user.completed_application_count += 1
    session.add(current_user)
    session.commit()
    session.refresh(row)
    return row


@router.post("/applications/prepare-options", response_model=Application)
def prepare_with_options(
    payload: PrepareApplicationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Application:
    job = session.get(Job, payload.job_id)
    profile = session.get(CareerProfile, payload.professional_profile_id)
    resume = session.get(ResumeDocument, payload.resume_id) if payload.resume_id else None
    if not job or not profile or profile.user_id != current_user.id:
        raise HTTPException(404, "Required record not found")
    if resume and resume.user_id != current_user.id:
        raise HTTPException(403, "Resume does not belong to user")

    return prepare_application(
        session,
        current_user,
        job,
        profile,
        resume,
        customize_resume=payload.customize_resume,
        generate_cover_letter=payload.generate_cover_letter,
        application_mode=payload.application_mode,
    )
