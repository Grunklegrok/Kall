import pytest
from fastapi import HTTPException
from kall.models.core import User
from kall.models.enums import SubscriptionPlan
from kall.services.quota import assert_application_allowed


def test_free_user_has_ten_applications() -> None:
    user = User(email="a@example.com", full_name="A", completed_application_count=9)
    assert_application_allowed(user)


def test_free_user_blocked_after_ten() -> None:
    user = User(
        email="a@example.com",
        full_name="A",
        completed_application_count=10,
        plan=SubscriptionPlan.FREE,
    )
    with pytest.raises(HTTPException) as exc:
        assert_application_allowed(user)
    assert exc.value.status_code == 402


def test_plus_user_is_unlimited() -> None:
    user = User(
        email="a@example.com",
        full_name="A",
        completed_application_count=100,
        plan=SubscriptionPlan.PLUS,
    )
    assert_application_allowed(user)
