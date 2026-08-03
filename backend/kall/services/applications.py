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
    *,
    customize_resume: bool = True,
    generate_cover_letter: bool = True,
    application_mode: str = "assisted",
) -> Application:
    assert_application_allowed(user)
    generated_dir = Path("generated") / str(user.id) / f"{job.company}-{job.id}"
    generated_dir.mkdir(parents=True, exist_ok=True)

    base_text = ""
    if resume:
        base_text = resume.extracted_text or extract_resume_text(resume.file_path, resume.mime_type)

    tailored_path: Path | None = None
    if customize_resume:
        tailored_path = generated_dir / "tailored_resume.txt"
        tailored_path.write_text(
            f"TARGET ROLE\n{job.title} at {job.company}\n\n"
            f"BASE RESUME\n{base_text}\n\n"
            "TAILORING NOTE\nPreserve factual accuracy. Emphasize requirements present in the posting.",
            encoding="utf-8",
        )

    cover_letter_path: Path | None = None
    if generate_cover_letter:
        cover_letter_path = generated_dir / "cover_letter.txt"
        cover_letter_path.write_text(
            f"Dear Hiring Team,\n\n"
            f"I am applying for the {job.title} role at {job.company}. "
            "This draft must be reviewed for factual accuracy and personalized before submission.\n\n"
            "Sincerely,\nCandidate",
            encoding="utf-8",
        )

    application = Application(
        user_id=user.id,
        job_id=job.id,
        career_profile_id=career_profile.id,
        base_resume_id=resume.id if resume else None,
        customized_resume_path=str(tailored_path) if tailored_path else None,
        cover_letter_path=str(cover_letter_path) if cover_letter_path else None,
        status=ApplicationStatus.REVIEW_REQUIRED,
        prepared_payload={
            "company": job.company,
            "title": job.title,
            "job_url": job.url,
            "resume_path": str(tailored_path) if tailored_path else (resume.file_path if resume else None),
            "cover_letter_path": str(cover_letter_path) if cover_letter_path else None,
            "customize_resume": customize_resume,
            "generate_cover_letter": generate_cover_letter,
            "application_mode": application_mode,
            "submission_policy": "Explicit review and approval are required before any submission.",
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