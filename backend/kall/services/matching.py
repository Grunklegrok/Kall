import re

from kall.models.core import CareerProfile, Job


def deterministic_match(job: Job, profile: CareerProfile) -> tuple[int, list[str], list[str]]:
    text = f"{job.title} {job.description}".lower()
    score = 0
    strengths: list[str] = []
    gaps: list[str] = []

    title_hits = [title for title in profile.target_titles if title.lower() in job.title.lower()]
    if title_hits:
        score += 35
        strengths.append(f"Target-title alignment: {title_hits[0]}")

    industry_hits = [i for i in profile.industries if i.lower() in text]
    if industry_hits:
        score += 15
        strengths.append(f"Industry alignment: {industry_hits[0]}")

    keyword_hits = [k for k in profile.include_keywords if k.lower() in text]
    score += min(30, len(keyword_hits) * 10)
    strengths.extend(f"Relevant: {k}" for k in keyword_hits[:4])

    excluded = [k for k in profile.exclude_keywords if k.lower() in text]
    if excluded:
        score -= min(30, len(excluded) * 10)
        gaps.extend(f"Excluded signal: {k}" for k in excluded[:3])

    if job.work_type and job.work_type.value in profile.work_types:
        score += 10
        strengths.append(f"Work style: {job.work_type.value}")

    if profile.minimum_base and job.salary_max and job.salary_max < profile.minimum_base:
        score -= 20
        gaps.append("Maximum disclosed salary is below minimum target")
    elif profile.minimum_base and job.salary_min and job.salary_min >= profile.minimum_base:
        score += 10
        strengths.append("Compensation meets minimum target")

    return max(0, min(100, score)), strengths, gaps


def salary_from_text(text: str) -> tuple[int | None, int | None]:
    values = [int(v.replace(",", "")) for v in re.findall(r"\$([0-9]{2,3}(?:,[0-9]{3})?)", text)]
    if not values:
        return None, None
    annual = [v * 1000 if v < 1000 else v for v in values]
    return min(annual), max(annual)
