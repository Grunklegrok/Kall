from fastapi import HTTPException
from kall.config import get_settings


def create_checkout_url(user_id: int) -> str:
    settings = get_settings()
    if not all([settings.stripe_secret_key, settings.stripe_price_id]):
        raise HTTPException(status_code=503, detail="Stripe is not configured")
    import stripe
    stripe.api_key = settings.stripe_secret_key
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url=f"{settings.frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.frontend_url}/billing",
        client_reference_id=str(user_id),
    )
    return session.url
