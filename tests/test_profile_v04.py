from kall.models.enums import PrivacyScope
from kall.profile_api import EEOProfilePayload, OnboardingPayload, PrivacyPayload


def test_onboarding_payload_defaults() -> None:
    payload = OnboardingPayload(current_step="identity")
    assert payload.completed_steps == []
    assert payload.is_complete is False


def test_sensitive_privacy_payload_requires_confirmation() -> None:
    payload = PrivacyPayload(
        field_path="eeo.veteran_status",
        scopes=[PrivacyScope.AUTOFILL],
    )
    assert payload.require_confirmation is True


def test_eeo_payload_defaults_to_confirmation() -> None:
    payload = EEOProfilePayload(veteran_status="decline_to_answer")
    assert payload.confirmation_required is True
