from datetime import datetime
from pathlib import Path

from kall.models import Application, CareerProfile, Job, ResumeDocument, User
from kall.models.enums import ApplicationStatus
from kall.services.quota import assert_application_allowed
from kall.services.resume import extract_resume_text
from sqlmodel import Session


def prepare_application(
    session: Session,
    user: User,
    job: Job,
    career_profile: CareerProfile,
    resume: ResumeDocument | None,
) -> Application:
    assert_application_allowed(user)
    generated_dir = Path("generated") / str(user.id) / f"{job.company}-{job.id}"
    generated_dir.mkdir(parents=True, exist_ok=True)

    base_text = ""
    if resume:
        base_text = resume.extracted_text or extract_resume_text(resume.file_path, resume.mime_type)

    tailored_path = generated_dir / "tailored_resume.txt"
    tailored_path.write_text(
        f"TARGET ROLE\n{job.title} at {job.company}\n\n"
        f"BASE RESUME\n{base_text}\n\n"
        "TAILORING NOTE\nPreserve factual accuracy. Emphasize requirements present in the posting.",
        encoding="utf-8",
    )

    application = Application(
        user_id=user.id,
        job_id=job.id,
        career_profile_id=career_profile.id,
        base_resume_id=resume.id if resume else None,
        customized_resume_path=str(tailored_path),
        status=ApplicationStatus.REVIEW_REQUIRED,
        prepared_payload={
            "company": job.company,
            "title": job.title,
            "job_url": job.url,
            "resume_path": str(tailored_path),
        },
        unanswered_questions=["Confirm application-specific screening questions"],
        sensitive_fields_present=True,
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


def approve_application(
    session: Session,
    application: Application,
    confirmed_sensitive_fields: bool,
    confirmed_answers: bool,
) -> Application:
    if application.sensitive_fields_present and not confirmed_sensitive_fields:
        raise ValueError("Sensitive fields require explicit confirmation")
    if application.unanswered_questions and not confirmed_answers:
        raise ValueError("Application-specific answers require explicit confirmation")
    application.status = ApplicationStatus.APPROVED
    application.user_approved_at = datetime.utcnow()
    session.add(application)
    session.commit()
    session.refresh(application)
    return application
