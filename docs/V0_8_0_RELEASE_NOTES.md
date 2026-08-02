# Kall v0.8.0

Kall v0.8 adds an explicit application-review layer between preparation and any future ATS submission connector.

## Included

- Screening-question extraction from prepared application payloads
- Suggested answer records with evidence and confidence metadata
- Accept, edit, and reject decisions
- Sensitive-category detection for EEO, veteran, disability, demographic, and work-authorization questions
- Document, answer, sensitive-field, and attestation confirmations
- Readiness issues and approval state
- Ownership-protected APIs and audit records
- Dark Nordic application-review workspace

## Safety boundary

Approval marks the application package as user-reviewed. It does not submit the application. Submission remains a separate connector capability and must verify approval, connector support, quotas, and current user intent.
