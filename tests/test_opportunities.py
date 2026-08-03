from datetime import datetime, timedelta

from kall.models import DiscoverySchedule, Job, Opportunity
from kall.services.opportunities import (
    canonical_key,
    due_schedule,
    mark_state,
    material_fingerprint,
)


def sample_job() -> Job:
    return Job(source="greenhouse", company="Example Games", title="Senior Environment Artist", description="Build worlds with Unreal Engine.", url="https://example.test/job/1", location="Remote")


def test_canonical_key_is_stable_across_formatting() -> None:
    first = sample_job()
    second = sample_job()
    second.company = " Example   Games "
    second.title = "Senior-Environment Artist"
    assert canonical_key(first) == canonical_key(second)


def test_material_change_changes_fingerprint() -> None:
    job = sample_job()
    before = material_fingerprint(job)
    job.description += " Lead a team."
    assert material_fingerprint(job) != before


def test_dismissal_records_fingerprint() -> None:
    row = Opportunity(user_id=1, professional_profile_id=1, job_id=1, canonical_key="key", material_fingerprint="fingerprint")
    mark_state(row, "not_interested")
    assert row.state == "not_interested"
    assert row.dismissed_fingerprint == "fingerprint"


def test_running_schedule_is_not_due() -> None:
    schedule = DiscoverySchedule(user_id=1, professional_profile_id=1, next_run_at=datetime.utcnow() - timedelta(hours=1), running_since=datetime.utcnow())
    assert due_schedule(schedule, datetime.utcnow()) is False
