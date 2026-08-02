# Kall Engineering Contract

**Version:** 1.0 Alpha  
**Status:** Authoritative

## System Shape

Kall is a multi-surface product with a shared domain model:

- Web application
- Desktop application
- Mobile application
- Backend APIs
- Career Graph data layer
- AI orchestration and deterministic analysis
- Integrations, notifications, billing, and search

## Current API Contracts

All user-owned endpoints require authentication and enforce ownership.

### `GET /api/me/morning-brief`

Returns a grounded daily summary assembled from stored Career Profiles, resumes, job matches, jobs, and applications. Deterministic Career Health dimensions must be explainable. Empty sources produce setup actions rather than fabricated activity.

### `GET /api/me/applications`

Returns the signed-in user's supported pipeline states, summary metrics, review queue, and next decision. Unsupported interview and offer stages must not be synthesized.

### `GET /api/me/resume-studio`

Returns owned resumes, metadata-completeness readiness checks, and Career Profile default-resume assignments.

### `PUT /api/me/professional-profiles/{profile_id}/default-resume`

Updates a Career Profile's default resume after validating ownership of both records.

### `GET /api/me/career-profiles`

Returns owned career strategies, deterministic completeness, stored match activity, best match, and default-resume context.

### `PUT /api/me/career-profiles/{profile_id}`

Updates owned strategy fields with bounded numeric inputs and schema validation.

## Contract Rules

- No endpoint may expose records owned by another user.
- Derived values identify their calculation basis.
- Heuristics are not labeled as AI predictions or guarantees.
- Sensitive fields are encrypted and excluded from public scope.
- API errors use actionable status codes and messages.
- Front ends provide loading, empty, error, and signed-out states for every endpoint.
- New breaking API behavior requires a documented migration plan.

## Frontend Contract

- Shared app navigation uses consistent domain names: Brief, Opportunities, Applications, Documents or Resume Studio, and Career.
- Design tokens map to the Figma Kall system.
- Components are accessible, responsive, and testable in isolation.
- Preview data must be visibly labeled and removed when a live contract exists.

## Quality Gates

- Type checking and linting.
- Backend unit and API tests.
- Frontend component and route tests.
- Contract tests between API responses and clients.
- Accessibility checks.
- Ownership and authorization tests.
- Deterministic heuristic regression tests.
- End-to-end coverage for the canonical MVP journey.

## Versioning

The FastAPI application version reflects meaningful API capability changes. Documentation changes should accompany endpoint additions or behavior changes in the same pull request whenever practical.