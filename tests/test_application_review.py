from kall.models import Application
from kall.services.application_review import SENSITIVE_CATEGORIES, detect_questions


def test_detect_questions_marks_sensitive_categories() -> None:
    application = Application(
        user_id=1,
        job_id=1,
        career_profile_id=1,
        prepared_payload={
            "screening_questions": [
                {"key": "visa", "prompt": "Will you require sponsorship?", "category": "work_authorization"},
                {"key": "why", "prompt": "Why this company?", "category": "general"},
            ]
        },
    )
    questions = detect_questions(application)
    assert questions[0]["sensitive"] is True
    assert questions[1]["sensitive"] is False


def test_sensitive_categories_include_eeo() -> None:
    assert "eeo" in SENSITIVE_CATEGORIES
    assert "veteran" in SENSITIVE_CATEGORIES


def test_empty_prompts_are_discarded() -> None:
    application = Application(
        user_id=1,
        job_id=1,
        career_profile_id=1,
        prepared_payload={"screening_questions": [{"key": "empty"}]},
    )
    assert detect_questions(application) == []
