from urllib.parse import quote_plus

from kall.models import CareerProfile

ATS_DOMAINS = [
    ("Ashby", "jobs.ashbyhq.com"),
    ("Greenhouse", "boards.greenhouse.io"),
    ("Lever", "jobs.lever.co"),
    ("iCIMS", "careers.icims.com"),
    ("Jobvite", "jobs.jobvite.com"),
    ("Workday", "myworkdayjobs.com"),
    ("BambooHR", "jobs.bamboohr.com"),
    ("SmartRecruiters", "jobs.smartrecruiters.com"),
    ("JazzHR", "apply.jazz.co"),
    ("Workable", "careers.workable.com"),
]


def _quoted_or(values: list[str], limit: int = 8) -> str:
    cleaned = [value.strip() for value in values if value and value.strip()]
    return " OR ".join(f'"{value}"' for value in cleaned[:limit])


def build_ats_queries(profile: CareerProfile) -> list[dict[str, object]]:
    titles = _quoted_or(profile.target_titles)
    keywords = _quoted_or(profile.include_keywords, limit=5)
    locations = _quoted_or([*profile.states_regions, *profile.countries], limit=5)
    exclusions = " ".join(f'-"{value.strip()}"' for value in profile.exclude_keywords[:5] if value.strip())

    intent_parts = []
    if titles:
        intent_parts.append(f"({titles})")
    if keywords:
        intent_parts.append(f"({keywords})")
    if locations:
        intent_parts.append(f"({locations})")
    if "remote" in {str(value).lower() for value in profile.work_types}:
        intent_parts.append('(remote OR "work from home")')
    if exclusions:
        intent_parts.append(exclusions)

    intent = " ".join(intent_parts).strip() or f'"{profile.name}"'
    site_clause = " OR ".join(f"site:{domain}" for _, domain in ATS_DOMAINS)
    query = f"({site_clause}) {intent}".strip()

    return [
        {
            "provider": "ATS Search",
            "domain": "10 ATS platforms",
            "domains": [domain for _, domain in ATS_DOMAINS],
            "providers": [provider for provider, _ in ATS_DOMAINS],
            "query": query,
            "google_url": f"https://www.google.com/search?q={quote_plus(query)}",
            "bing_url": f"https://www.bing.com/search?q={quote_plus(query)}",
        }
    ]
