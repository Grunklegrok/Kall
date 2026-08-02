from enum import StrEnum


class PrivacyScope(StrEnum):
    PRIVATE = "private"
    TAILORING = "tailoring"
    AUTOFILL = "autofill"
    PUBLIC_PROFILE = "public_profile"


class WorkType(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "on_site"


class ApplicationStatus(StrEnum):
    DISCOVERED = "discovered"
    PREPARING = "preparing"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"


class SubscriptionPlan(StrEnum):
    FREE = "free"
    PLUS = "plus"


class Proficiency(StrEnum):
    BASIC = "basic"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    NATIVE = "native"
