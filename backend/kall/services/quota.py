from fastapi import HTTPException
from kall.models.core import User
from kall.models.enums import SubscriptionPlan
from sqlmodel import Session

FREE_COMPLETED_APPLICATION_LIMIT = 10


def assert_application_allowed(user: User) -> None:
    if (
        user.plan == SubscriptionPlan.FREE
        and user.completed_application_count >= FREE_COMPLETED_APPLICATION_LIMIT
    ):
        raise HTTPException(
            status_code=402,
            detail={
                "code": "subscription_required",
                "message": "The first 10 completed applications are free. Upgrade to Plus for $4/month.",
            },
        )


def record_completed_application(session: Session, user: User) -> None:
    user.completed_application_count += 1
    session.add(user)
    session.commit()
