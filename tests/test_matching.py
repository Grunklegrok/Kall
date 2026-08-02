from kall.models.core import CareerProfile, Job
from kall.models.enums import WorkType
from kall.services.matching import deterministic_match


def test_matching_rewards_title_keywords_remote_and_salary() -> None:
    profile = CareerProfile(
        user_id=1,
        name="Executive Engineering",
        target_titles=["Director of Quality Engineering"],
        industries=["SaaS"],
        include_keywords=["automation strategy", "CI/CD"],
        exclude_keywords=["manual tester"],
        work_types=["remote"],
        minimum_base=180000,
    )
    job = Job(
        source="test",
        company="Example",
        title="Director of Quality Engineering",
        description="SaaS leader for automation strategy and CI/CD.",
        url="https://example.com/job/1",
        work_type=WorkType.REMOTE,
        salary_min=190000,
        salary_max=230000,
    )
    score, strengths, gaps = deterministic_match(job, profile)
    assert score >= 85
    assert not gaps
