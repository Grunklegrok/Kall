import pytest
from kall.models import Application
from kall.models.enums import ApplicationStatus
from kall.services.applications import approve_application
from sqlmodel import Session, SQLModel, create_engine


def test_sensitive_application_requires_confirmation() -> None:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        app = Application(
            user_id=1,
            job_id=1,
            career_profile_id=1,
            status=ApplicationStatus.REVIEW_REQUIRED,
            sensitive_fields_present=True,
            unanswered_questions=[],
        )
        session.add(app)
        session.commit()
        session.refresh(app)
        with pytest.raises(ValueError):
            approve_application(session, app, False, True)
