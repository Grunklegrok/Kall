import re
from collections import Counter
from datetime import datetime, timezone

from sqlmodel import Session, delete, select

from kall.models import (
    Achievement,
    AchievementJobMatch,
    CareerProfile,
    Job,
    JobRequirementAnalysis,
    RequirementEvidence,
    ResumeDocument,
    ResumeJobScore,
    ResumeParse,
    ResumeSelection,
)

SCORING_VERSION = "resume-match-v1"
ACHIEVEMENT_SCORING_VERSION = "achievement-match-v1"


def _tokens(value: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{1,}", value or "")
        if token.lower() not in {"and", "the", "with", "for", "from", "that", "this"}
    }


def _overlap(left: set[str], right: set[str]) -> int:
    return len(left & right)


def _latest_parse(session: Session, resume_id: int) -> ResumeParse | None:
    return session.exec(
        select(ResumeParse)
        .where(ResumeParse.resume_id == resume_id)
        .order_by(ResumeParse.created_at.desc())
    ).first()


def _resume_text(resume: ResumeDocument, parse: ResumeParse | None) -> str:
    if parse:
        sections = parse.parsed_json.get("sections", {})
        return "\n".join(
            "\n".join(lines) if isinstance(lines, list) else str(lines)
            for lines in sections.values()
        )
    return resume.extracted_text or ""


def _job_requirements(analysis: JobRequirementAnalysis) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    items.extend((item, "required_skill") for item in analysis.required_skills)
    items.extend((item, "preferred_skill") for item in analysis.preferred_skills)
    items.extend((item, "education") for item in analysis.education_requirements)
    items.extend((item, "certification") for item in analysis.certification_requirements)
    return items


def rank_resumes(
    session: Session,
    user_id: int,
    job: Job,
    profile: CareerProfile,
    analysis: JobRequirementAnalysis,
) -> list[ResumeJobScore]:
    session.exec(delete(ResumeJobScore).where(ResumeJobScore.user_id == user_id, ResumeJobScore.job_id == job.id))
    session.exec(delete(RequirementEvidence).where(RequirementEvidence.user_id == user_id, RequirementEvidence.job_id == job.id))

    verified = list(session.exec(select(Achievement).where(Achievement.user_id == user_id, Achievement.verification_status == "verified")))
    resumes = list(session.exec(select(ResumeDocument).where(ResumeDocument.user_id == user_id)))
    requirement_tokens = _tokens(" ".join(analysis.required_skills + analysis.preferred_skills + analysis.ats_keywords))
    job_tokens = _tokens(f"{job.title} {job.description}")
    scores: list[ResumeJobScore] = []

    for resume in resumes:
        parse = _latest_parse(session, resume.id)
        text = _resume_text(resume, parse)
        resume_tokens = _tokens(text)
        title_hits = max((_overlap(_tokens(title), _tokens(job.title)) for title in resume.target_titles), default=0)
        title_score = min(20, title_hits * 5)
        industry_hits = sum(1 for industry in resume.industries if industry.lower() in job.description.lower())
        industry_score = min(10, industry_hits * 5)
        covered = requirement_tokens & resume_tokens
        skills_score = min(35, round(35 * len(covered) / max(1, len(requirement_tokens))))
        leadership_terms = {"director", "head", "lead", "manager", "strategy", "executive", "team"}
        leadership_score = min(10, _overlap(resume_tokens, leadership_terms & job_tokens) * 2)
        current_year = datetime.now(timezone.utc).year
        years = [int(value) for value in re.findall(r"\b(20\d{2})\b", text)]
        recency_score = 10 if years and max(years) >= current_year - 2 else 5 if years else 0

        matched_achievements = []
        for achievement in verified:
            overlap = _overlap(_tokens(achievement.achievement_text + " " + " ".join(achievement.skills)), job_tokens)
            if overlap:
                matched_achievements.append((achievement, overlap))
        achievement_score = min(10, sum(min(3, overlap) for _, overlap in matched_achievements))
        default_boost = 5 if profile.default_resume_id == resume.id or resume.is_default else 0
        total = min(100, title_score + industry_score + skills_score + leadership_score + recency_score + achievement_score + default_boost)

        explanation = []
        if covered:
            explanation.append(f"Covers {len(covered)} job keywords")
        if matched_achievements:
            explanation.append(f"Links to {len(matched_achievements)} verified achievements")
        if default_boost:
            explanation.append("Receives a limited default-resume preference boost")
        gaps = sorted(requirement_tokens - resume_tokens)[:12]

        row = ResumeJobScore(
            user_id=user_id,
            job_id=job.id,
            resume_id=resume.id,
            professional_profile_id=profile.id,
            total_score=total,
            title_score=title_score,
            industry_score=industry_score,
            skills_score=skills_score,
            leadership_score=leadership_score,
            recency_score=recency_score,
            achievement_score=achievement_score,
            default_resume_boost=default_boost,
            explanation=explanation,
            gaps=gaps,
            evidence_summary={"covered_keywords": sorted(covered), "missing_keywords": gaps},
        )
        session.add(row)
        scores.append(row)

        for requirement, requirement_type in _job_requirements(analysis):
            req_tokens = _tokens(requirement)
            matched = bool(req_tokens & resume_tokens)
            session.add(
                RequirementEvidence(
                    user_id=user_id,
                    job_id=job.id,
                    resume_id=resume.id,
                    requirement=requirement,
                    requirement_type=requirement_type,
                    evidence_status="verified" if matched else "missing",
                    evidence_source="resume" if matched else None,
                    evidence_text=requirement if matched else None,
                    confidence=90 if matched else 0,
                )
            )

    scores.sort(key=lambda item: (-item.total_score, item.resume_id))
    recommended_id = scores[0].resume_id if scores else None
    selection = session.exec(
        select(ResumeSelection).where(
            ResumeSelection.user_id == user_id,
            ResumeSelection.job_id == job.id,
            ResumeSelection.professional_profile_id == profile.id,
        )
    ).first()
    if not selection:
        selection = ResumeSelection(
            user_id=user_id,
            job_id=job.id,
            professional_profile_id=profile.id,
            recommended_resume_id=recommended_id,
            selected_resume_id=recommended_id,
        )
    else:
        selection.recommended_resume_id = recommended_id
        if selection.selection_source != "user_override":
            selection.selected_resume_id = recommended_id
    session.add(selection)

    session.exec(delete(AchievementJobMatch).where(AchievementJobMatch.user_id == user_id, AchievementJobMatch.job_id == job.id))
    for achievement in verified:
        matched = sorted(_tokens(achievement.achievement_text + " " + " ".join(achievement.skills)) & job_tokens)
        if not matched:
            continue
        session.add(
            AchievementJobMatch(
                user_id=user_id,
                job_id=job.id,
                achievement_id=achievement.id,
                score=min(100, len(matched) * 10 + min(20, len(achievement.metrics) * 5)),
                matched_requirements=matched,
                explanation=["Uses verified achievement evidence", f"Matches {len(matched)} job terms"],
            )
        )

    session.commit()
    for score in scores:
        session.refresh(score)
    return scores


def coverage_summary(evidence: list[RequirementEvidence]) -> dict:
    counts = Counter(item.requirement_type for item in evidence)
    covered = Counter(item.requirement_type for item in evidence if item.evidence_status != "missing")
    return {
        key: {"covered": covered[key], "total": counts[key]}
        for key in sorted(counts)
    }
