# Kall MVP Requirements

**Version:** 1.0 Alpha  
**Status:** Authoritative baseline

## MVP Objective

Deliver a coherent first-run journey in which a user can establish a career strategy, upload and organize resumes, receive a grounded Morning Brief, evaluate opportunities, and manage applications with review-before-submit controls.

## Canonical User Journey

Sign in → Onboarding → Career Profile → Resume Studio → Morning Brief → Opportunity Review → Applications

## Implemented Alpha Modules

### Integrated Onboarding

Purpose: move a new user from account creation to a useful, grounded Morning Brief without routing them through disconnected legacy screens.

Required behavior:

- Create the account and persist the authenticated session.
- Guide the user through one initial Career Profile with target roles, work modes, geography, keywords, and compensation preferences.
- Offer a factual resume upload using the existing Resume Studio ingestion contract.
- Allow resume upload to be skipped without blocking access to Kall.
- Summarize which foundation records were created before entering the Morning Brief.
- Send users to Career Profiles or Resume Studio when skipped setup remains incomplete.
- Never claim that profile analysis, opportunity matching, or resume readiness exists until supported records are stored.

### Morning Brief

Purpose: provide a calm, personalized starting point that answers what deserves attention today.

Required behavior:

- Use authenticated user data.
- Summarize career-profile readiness, resume readiness, opportunity activity, and application momentum.
- Present one clear recommended next action.
- Provide signed-out, loading, empty, and error states.
- Never fabricate recruiter views, interviews, offers, or external activity.

### Career Profiles

Purpose: allow users to maintain distinct career strategies rather than one undifferentiated job search.

Required fields:

- Strategy name and active state.
- Target titles, industries, and functional areas.
- Include and exclude keywords.
- Countries, states or regions, and work modes.
- Minimum, target, stretch, and total compensation preferences.
- Travel and relocation preferences.
- Default resume assignment.

Required behavior:

- Support multiple profiles per user.
- Enforce ownership on reads and updates.
- Show deterministic strategy completeness.
- Show stored match activity and best match where records exist.

### Resume Studio

Purpose: provide a reusable library of career documents organized by strategy and purpose.

Required behavior:

- List owned resumes with versions, tags, industries, titles, and timestamps.
- Show deterministic metadata completeness as readiness; do not present it as an ATS or hiring prediction.
- Allow a default resume to be assigned independently to each Career Profile.
- Provide empty-library, signed-out, loading, and error states.
- Preserve source content and version history.

### Opportunities and Job Intelligence

Purpose: help users decide whether an opportunity advances their career strategy.

Required behavior:

- Explain strengths, gaps, and match evidence.
- Distinguish stored facts from heuristic analysis.
- Link the opportunity to the relevant Career Profile and resume.
- Present compensation and work-location context when available.
- Avoid unsupported claims about hiring likelihood.

### Applications Workspace

Current supported states:

- Preparing
- Needs Review
- Approved
- Submitted
- Closed

Required behavior:

- Display only stored application records and supported states.
- Surface unanswered questions, sensitive fields, and claims needing confirmation.
- Never approve or submit without user confirmation.
- Provide an explicit next-decision area and true empty-pipeline state.

### Candidate Profile and Privacy

Required behavior:

- Support education, skills, certifications, languages, clearances, awards, publications, patents, speaking, memberships, volunteer or board service, references, work authorization, and EEO data.
- Protect sensitive data through encryption and field-level scopes.
- Allow fields to be private, available for tailoring, available for autofill, or eligible for a public profile when appropriate.
- Prevent sensitive EEO, authorization, and reference fields from becoming public.

## Platform Requirements

- Authentication is required for user-owned workspaces.
- Every major screen provides loading, empty, error, and signed-out states.
- Ownership checks apply to every mutable record.
- Accessibility target is WCAG 2.2 AA.
- Web, desktop, and mobile share the same domain language and design tokens.
- Consequential AI actions require review and auditability.

## Post-MVP Scope

The following are planned and must not be represented as implemented:

- Interview-stage records and interview workspace.
- Offer, negotiation, accepted, and declined offer stages.
- Recruiter and hiring-manager workspaces.
- Public recruiter-searchable career sites.
- Enterprise administration.
- Mentorship and networking ecosystems.
- Learning marketplace.

## MVP Exit Criteria

A user can complete the canonical journey with real stored data, understand why Kall recommends an action, and remain in control of all consequential career and application decisions.
