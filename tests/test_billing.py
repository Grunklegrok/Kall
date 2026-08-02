from kall.services.billing import FREE_APPLICATION_LIMIT


def test_free_application_limit_is_ten():
    assert FREE_APPLICATION_LIMIT == 10


def test_plus_plan_statuses_are_explicit():
    from kall.services.billing import ACTIVE_STATUSES

    assert ACTIVE_STATUSES == {"active", "trialing"}


def test_billing_routes_are_registered():
    from kall.main import app

    paths = {route.path for route in app.routes}
    assert "/api/billing/status" in paths
    assert "/api/billing/checkout" in paths
    assert "/api/billing/portal" in paths
    assert "/api/billing/webhook" in paths
