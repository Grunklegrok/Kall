# Integration workflow

Kall uses one active product milestone branch at a time. New branches must start from the latest `main` after the preceding milestone merges.

## Shared integration points

- Add API routers in `backend/kall/router_registry.py`; keep `main.py` stable.
- Every migration must reference the current single Alembic head.
- Feature pull requests do not update `VERSION`. Version changes belong in a dedicated release pull request.
- Run `pytest tests/test_integration_contracts.py` before opening a pull request.

## Testimonial safety

Invitation owners may revoke pending requests. Authors may withdraw completed testimonials using the original invitation token. Withdrawal immediately disables profile and application use and cannot be overridden through moderation.
