from alembic.config import Config
from alembic.script import ScriptDirectory

from kall.main import app
from kall.router_registry import API_ROUTERS


def test_router_registry_is_complete() -> None:
    paths = {route.path for route in app.routes}
    expected = {
        "/api/testimonials/requests",
        "/api/testimonials/profile-card",
        "/api/applications/{application_id}/review",
        "/api/opportunities",
    }
    assert expected.issubset(paths)
    assert len(API_ROUTERS) >= 12


def test_alembic_revision_chain_is_complete_and_has_single_head() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    # Walking from each head forces Alembic to resolve every down_revision.
    # This catches missing intermediate migration files, not just split heads.
    heads = script.get_heads()
    assert len(heads) == 1
    revisions = list(script.walk_revisions(base="base", head=heads[0]))
    revision_ids = {revision.revision for revision in revisions}

    assert "20260802_0007" in revision_ids
    assert "20260802_0013" in revision_ids
