# Kall

Kall is a privacy-first career identity, job discovery, application preparation, and application tracking platform.

This repository is a production-oriented MVP containing:

- FastAPI backend
- SQLModel data layer
- Career identity models
- Career profiles with industry/title/location/work-style selectors
- Resume library and tailoring workflow
- Education, skills, certifications, licenses, languages, clearances, awards, publications, patents, speaking, memberships, volunteer and board service
- Reusable references with permission controls
- EEO/work-authorization profile with field-level privacy rules
- Job search profiles with compensation targets
- Application preparation and review-before-submit workflow
- First 10 completed applications free, then a $4/month Stripe subscription gate
- Email and push-notification abstractions
- Web app starter
- Mobile app starter
- Tauri desktop wrapper starter
- Tests, Docker, CI, and seeded profile data derived from James Shattuck's supplied resume

## Important application-safety rule

Kall prepares and prefills applications, but it does **not** silently submit applications or sensitive EEO attestations. Every prepared application enters `review_required`, and the user must explicitly approve the final payload before an ATS connector may submit it.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

API docs: http://localhost:8000/docs  
Web app: http://localhost:3000

## Local backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn kall.main:app --reload
```

## Seed James's profile

```bash
python scripts/seed_james_profile.py
```

## Test

```bash
pytest
ruff check .
```

## Billing

The application quota service allows 10 completed applications on the free plan. Stripe checkout and webhook endpoints are included, but require Stripe environment variables.

## Repository status

This is a coherent MVP foundation. ATS-specific submission connectors are intentionally limited to a safe provider interface and a mock connector. Real provider adapters must be implemented only where the provider permits automated submission.


## Kall Search milestone

This release adds configurable Greenhouse, Lever and Ashby sources, normalized job ingestion, URL deduplication, salary/work-style inference, professional-profile matching, ranked feed APIs, and web pages for sources, profiles, jobs and application preparation.
