# Kall

Kall is a privacy-first career identity, job discovery, application preparation, and application tracking platform.

This repository is a production-oriented MVP containing identity profiles, professional profiles, Resume Studio, Greenhouse/Lever/Ashby discovery, matching, application preparation, field-level privacy, and subscription foundations.

## Safety rule

Kall prepares and prefills applications, but does not silently submit sensitive EEO attestations. Prepared applications require explicit review and approval before a supported ATS connector may submit them.

## Quick start

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn kall.main:app --reload
```

Run the web client separately:

```bash
cd apps/web
npm install
npm run dev
```

API docs: http://localhost:8000/docs
Web app: http://localhost:3000

## v0.3 stabilization

Kall v0.3 adds Alembic migrations, production environment validation, CORS configuration, logout and session revocation, password reset, email-verification tokens, login lockout protection, backend and web CI, PostgreSQL support, and a reproducible local-development guide.
