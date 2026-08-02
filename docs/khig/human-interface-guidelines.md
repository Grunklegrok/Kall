# Kall Human Interface Guidelines

**Version:** 1.0  
**Status:** Authoritative

## Experience Goal

Every screen should feel calm enough that a user could spend an hour there without fatigue.

## Principles

### Calm by Default

Avoid flashing alerts, artificial urgency, excessive badges, gamification, neon accents, and crowded dashboards. Prefer quiet summaries, deliberate pacing, and clear next actions.

### One Meaningful Decision Per Screen

Each screen has one primary question and one primary action. Secondary actions support rather than compete.

### Explain Every Recommendation

Recommendations must state what is suggested, why, what evidence was used, whether the output is fact, heuristic, or AI suggestion, and what the user can change.

### Respect Time

Kall prepares work before the user arrives. Users review and decide rather than repeatedly starting from scratch.

### Professional Dignity

Use measured, direct language. Avoid hype, pressure, celebration loops, or language that treats professionals as engagement metrics.

## Visual Language

- Dark-first graphite canvases and layered charcoal surfaces.
- Warm off-white primary text and muted secondary text.
- Restrained fjord-blue accent.
- Thin borders, low elevation, minimal decoration.
- Typography is the primary hierarchy.
- Motion clarifies state changes and remains subtle, generally 150–200 ms.

## Cross-Platform Behavior

- Web provides universal full access and responsive layouts.
- Desktop supports deep, keyboard-first work and denser information.
- Mobile prioritizes review, approval, notifications, and interview-day utility.
- Users should not need to relearn Kall when switching devices.

## Required States

Every major workspace must define:

- Loading
- Empty
- Error
- Signed-out or permission-denied
- Success confirmation
- Destructive-action confirmation where applicable

## Accessibility

- WCAG 2.2 AA minimum.
- Full keyboard navigation.
- Visible focus states.
- Screen-reader labels and semantic structure.
- Reduced-motion support.
- Scalable typography.
- Status never conveyed by color alone.

## AI Interaction

AI is proactive but not intrusive. It may prepare recommendations, summaries, tailoring, and interview materials. It may not invent qualifications, silently overwrite user facts, or execute consequential actions without appropriate review.

## Release Checklist

Before shipping, confirm the feature reduces anxiety, increases clarity, saves time, supports long-term career growth, explains intelligence, protects user control, meets accessibility requirements, and works appropriately across web, desktop, and mobile.