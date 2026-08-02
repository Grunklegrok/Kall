# ADR-0001: Repository-Authoritative Product Documentation

**Status:** Accepted  
**Date:** 2026-08-02

## Context

Kall's product requirements, design guidance, and implementation evolved across conversation history, Notion, Figma, and GitHub. The implementation moved faster than the external documentation, creating drift and making it difficult to verify which behavior was planned versus implemented.

## Decision

The `docs/` directory in `Grunklegrok/Kall` is the authoritative source for product requirements, human-interface guidance, engineering contracts, architecture decisions, and roadmap status.

Figma remains the visual source of truth for layouts, components, tokens, and prototypes. Notion may be used as a collaboration or publishing layer, but it is not authoritative unless its changes are synchronized into the repository.

## Consequences

- Product and engineering documentation can be reviewed and versioned with code.
- Feature pull requests should update relevant documentation.
- Documentation history is auditable.
- Figma links and visual specifications may be referenced from repository documents.
- Any future Notion synchronization must preserve repository content and version history.

## Governance

Material changes to product behavior, architecture, or interface principles require an update to the relevant document or a new ADR.