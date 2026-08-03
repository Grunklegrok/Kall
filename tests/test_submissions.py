from fastapi.routing import APIRoute
from kall.services.submissions import checksum


def _app_paths(app) -> set[str]:
    """Return all registered route paths, including those in included sub-routers."""
    paths: set[str] = set()
    for r in app.routes:
        if isinstance(r, APIRoute):
            paths.add(r.path)
        elif hasattr(r, "include_context") and hasattr(r, "original_router"):
            prefix = r.include_context.prefix or ""
            for sub in r.original_router.routes:
                if isinstance(sub, APIRoute):
                    paths.add(prefix + sub.path)
    return paths


def test_preview_checksum_is_deterministic():
    assert checksum({"b": 2, "a": 1}) == checksum({"a": 1, "b": 2})


def test_preview_checksum_changes_with_content():
    assert checksum({"a": 1}) != checksum({"a": 2})


def test_submission_routes_registered():
    from kall.main import app
    paths = _app_paths(app)
    assert "/api/applications/{application_id}/submission-preview" in paths
    assert "/api/submissions/{submission_id}/confirm" in paths
    assert "/api/submissions/{submission_id}/attempt" in paths
