from kall.services.submissions import checksum


def test_preview_checksum_is_deterministic():
    assert checksum({"b": 2, "a": 1}) == checksum({"a": 1, "b": 2})


def test_preview_checksum_changes_with_content():
    assert checksum({"a": 1}) != checksum({"a": 2})


def test_submission_routes_registered():
    from kall.main import app
    paths = {route.path for route in app.routes}
    assert "/api/applications/{application_id}/submission-preview" in paths
    assert "/api/submissions/{submission_id}/confirm" in paths
    assert "/api/submissions/{submission_id}/attempt" in paths
