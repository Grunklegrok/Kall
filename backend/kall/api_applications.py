from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from kall.auth import get_current_user
from kall.db import get_session
from kall.models import Application, Job, JobMatch, User
from kall.models.enums import ApplicationStatus

router = APIRouter()


_STAGE_MAP: dict[ApplicationStatus, str] = {
    ApplicationStatus.DISCOVERED: "preparing",
    ApplicationStatus.PREPARING: "preparing",
    ApplicationStatus.REVIEW_REQUIRED: "review",
    ApplicationStatus.APPROVED: "approved",
    ApplicationStatus.SUBMITTED: "submitted",
    ApplicationStatus.FAILED: "closed",
    ApplicationStatus.WITHDRAWN: "closed",
}

_STAGE_LABELS = {
    "preparing": "Preparing",
    "review": "Needs review",
    "approved": "Approved",
    "submitted": "Submitted",
    "closed": "Closed",
}


def _iso(value: datetime | None) -> str | None:
    if not value:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


@router.get("/me/applications")
def applications_pipeline(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    applications = list(
        session.exec(
            select(Application)
            .where(Application.user_id == current_user.id)
            .order_by(Application.updated_at.desc())
        )
    )

    job_ids = {row.job_id for row in applications}
    jobs = {
        row.id: row
        for row in session.exec(select(Job).where(Job.id.in_(job_ids)))
        if row.id is not None
    } if job_ids else {}

    matches = list(
        session.exec(select(JobMatch).where(JobMatch.user_id == current_user.id))
    )
    match_by_job: dict[int, JobMatch] = {}
    for match in matches:
        existing = match_by_job.get(match.job_id)
        if existing is None or match.score > existing.score:
            match_by_job[match.job_id] = match

    grouped: dict[str, list[dict]] = {key: [] for key in _STAGE_LABELS}
    counts: Counter[str] = Counter()

    for application in applications:
        stage = _STAGE_MAP[application.status]
        counts[stage] += 1
        job = jobs.get(application.job_id)
        match = match_by_job.get(application.job_id)
        grouped[stage].append(
            {
                "id": application.id,
                "status": application.status,
                "stage": stage,
                "company": job.company if job else "Unknown company",
                "role": job.title if job else "Unknown role",
                "location": job.location if job else None,
                "match_score": match.score if match else None,
                "updated_at": _iso(application.updated_at),
                "submitted_at": _iso(application.submitted_at),
                "requires_review": application.status == ApplicationStatus.REVIEW_REQUIRED,
                "unanswered_question_count": len(application.unanswered_questions),
                "sensitive_fields_present": application.sensitive_fields_present,
                "failure_reason": application.failure_reason,
            }
        )

    active_statuses = {
        ApplicationStatus.DISCOVERED,
        ApplicationStatus.PREPARING,
        ApplicationStatus.REVIEW_REQUIRED,
        ApplicationStatus.APPROVED,
        ApplicationStatus.SUBMITTED,
    }
    active = sum(row.status in active_statuses for row in applications)
    review_queue = grouped["review"]
    next_decision = review_queue[0] if review_queue else None
    best_match = max(
        (item["match_score"] for items in grouped.values() for item in items if item["match_score"] is not None),
        default=None,
    )

    return {
        "summary": {
            "total": len(applications),
            "active": active,
            "needs_review": counts["review"],
            "submitted": counts["submitted"],
            "best_match": best_match,
        },
        "stages": [
            {
                "key": key,
                "label": label,
                "count": len(grouped[key]),
                "items": grouped[key],
            }
            for key, label in _STAGE_LABELS.items()
        ],
        "next_decision": next_decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
