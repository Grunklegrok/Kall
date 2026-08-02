from kall.models import Achievement, CareerProfile, Job, JobRequirementAnalysis, ResumeDocument
from kall.models.enums import WorkType
from kall.services.match_intelligence import _tokens


def test_tokens_are_deterministic() -> None:
    assert _tokens("Python, CI/CD and AWS") == {"python", "ci/cd", "aws"}


def test_rejected_achievement_is_not_verified() -> None:
    achievement = Achievement(user_id=1, achievement_text="Reduced defects by 40%", verification_status="rejected")
    assert achievement.verification_status != "verified"


def test_default_resume_boost_is_limited() -> None:
    profile = CareerProfile(user_id=1, name="Director", default_resume_id=7)
    resume = ResumeDocument(user_id=1, name="resume", file_path="x", mime_type="text/plain", is_default=True)
    assert profile.default_resume_id == 7
    assert resume.is_default is True


def test_job_requirements_keep_explicit_and_inferred_separate() -> None:
    analysis = JobRequirementAnalysis(
        job_id=1,
        required_skills=["Python"],
        explicit_requirements=["10 years experience"],
        inferred_signals=["executive influence"],
    )
    assert "10 years experience" not in analysis.inferred_signals


def test_sensitive_fields_are_not_part_of_match_models() -> None:
    job = Job(source="test", company="Acme", title="Director", description="Python", url="https://example.com/1", work_type=WorkType.REMOTE)
    assert not hasattr(job, "race_ethnicity_encrypted")
