from kall.models import Application
from kall.services.application_review import SENSITIVE_CATEGORIES, detect_questions


def test_sensitive_question_detection() -> None:
    application = Application(
        user_id=1,
        job_id=1,
        career_profile_id=1,
        prepared_payload={
            "screening_questions": [
                {"key": "visa", "prompt": "Will you need sponsorship?", "category": "work_authorization"},
                {"key": "why", "prompt": "Why this role?", "category": "general"},
            ]
        },
    )
    questions = detect_questions(application)
    assert questions[0]["sensitive"] is True
    assert questions[1]["sensitive"] is False
    assert "work_authorization" in SENSITIVE_CATEGORIES


def test_string_questions_are_normalized() -> None:
    application = Application(user_id=1, job_id=1, career_profile_id=1, prepared_payload={"screening_questions": ["Why Kall?"]})
    questions = detect_questions(application)
    assert questions[0]["prompt"] == "Why Kall?"
    assert questions[0]["required"] is True
