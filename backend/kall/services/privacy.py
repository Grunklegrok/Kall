from sqlmodel import Session, select
from kall.models.core import FieldPrivacy
from kall.models.enums import PrivacyScope


def field_allowed(session: Session, user_id: int, field_path: str, scope: PrivacyScope) -> bool:
    rule = session.exec(
        select(FieldPrivacy).where(
            FieldPrivacy.user_id == user_id,
            FieldPrivacy.field_path == field_path,
        )
    ).first()
    if not rule:
        return False
    return scope.value in rule.scopes
