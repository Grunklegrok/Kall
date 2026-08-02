import hashlib
import re
from collections import Counter
from datetime import datetime, timedelta

from sqlmodel import Session, select

from kall.models import (
    DiscoverySchedule,
    GrowthGoal,
    GrowthMarketSignal,
    Job,
    JobRequirementAnalysis,
    NotificationDelivery,
    NotificationPreference,
    Opportunity,
)


def normalize(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def canonical_key(job: Job) -> str:
    identity = "|".join([normalize(job.company), normalize(job.title), normalize(job.location)])
    return hashlib.sha256(identity.encode()).hexdigest()


def material_fingerprint(job: Job) -> str:
    content = "|".join([
        normalize(job.title), normalize(job.location), normalize(job.description),
        str(job.salary_min or ""), str(job.salary_max or ""), str(job.work_type or ""),
    ])
    return hashlib.sha256(content.encode()).hexdigest()


def upsert_opportunity(
    session: Session, *, user_id: int, profile_id: int, job: Job, match_score: int
) -> Opportunity:
    key = canonical_key(job)
    fingerprint = material_fingerprint(job)
    row = session.exec(select(Opportunity).where(
        Opportunity.user_id == user_id,
        Opportunity.professional_profile_id == profile_id,
        Opportunity.canonical_key == key,
    )).first()
    source = {"source": job.source, "external_id": job.external_id, "url": job.url}
    if row:
        row.last_seen_at = datetime.utcnow()
        row.match_score = max(row.match_score, match_score)
        row.source_records = list({item.get("url"): item for item in [*row.source_records, source]}.values())
        if row.state == "not_interested" and row.dismissed_fingerprint != fingerprint:
            row.state = "new"
        row.material_fingerprint = fingerprint
    else:
        row = Opportunity(
            user_id=user_id, professional_profile_id=profile_id, job_id=job.id,
            canonical_key=key, material_fingerprint=fingerprint, match_score=match_score,
            source_records=[source],
        )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def mark_state(row: Opportunity, state: str) -> Opportunity:
    allowed = {"new", "saved", "reviewing", "apply", "not_interested", "archived"}
    if state not in allowed:
        raise ValueError("Unsupported opportunity state")
    row.state = state
    if state == "not_interested":
        row.dismissed_fingerprint = row.material_fingerprint
    return row


def due_schedule(schedule: DiscoverySchedule, now: datetime) -> bool:
    return schedule.enabled and not schedule.running_since and (
        schedule.next_run_at is None or schedule.next_run_at <= now
    )


def advance_schedule(schedule: DiscoverySchedule, now: datetime) -> None:
    days = 7 if schedule.cadence == "weekly" else 1
    candidate = now + timedelta(days=days)
    if schedule.cadence == "weekdays":
        while candidate.weekday() >= 5:
            candidate += timedelta(days=1)
    schedule.last_run_at = now
    schedule.next_run_at = candidate
    schedule.running_since = None


def queue_digest(session: Session, user_id: int, opportunity_ids: list[int]) -> NotificationDelivery:
    date_key = datetime.utcnow().date().isoformat()
    delivery = NotificationDelivery(
        user_id=user_id, channel="email", kind="opportunity_digest",
        dedupe_key=f"digest:{user_id}:{date_key}",
        payload={"opportunity_ids": opportunity_ids},
    )
    session.add(delivery)
    session.commit()
    session.refresh(delivery)
    return delivery


def analyze_growth_market(session: Session, goal: GrowthGoal, analyses: list[JobRequirementAnalysis]) -> GrowthMarketSignal:
    skills: Counter[str] = Counter()
    requirements: Counter[str] = Counter()
    for analysis in analyses:
        skills.update(item.lower() for item in analysis.required_skills + analysis.preferred_skills)
        requirements.update(item.lower() for item in analysis.explicit_requirements)
    signal = GrowthMarketSignal(
        user_id=goal.user_id, growth_goal_id=goal.id, observed_jobs=len(analyses),
        recurring_skills=[{"name": key, "count": count} for key, count in skills.most_common(12)],
        recurring_requirements=[{"text": key, "count": count} for key, count in requirements.most_common(12)],
        portfolio_signals=[f"Create evidence demonstrating {key}" for key, _ in skills.most_common(3)],
    )
    session.add(signal)
    session.commit()
    session.refresh(signal)
    return signal
