from kall.models.core import Application
from kall.models.enums import ApplicationStatus


class MockATSConnector:
    name = "mock"

    def can_prepare(self, job_url: str) -> bool:
        return job_url.startswith("https://example.com/")

    def submit(self, application: Application) -> str:
        if application.status != ApplicationStatus.APPROVED:
            raise ValueError("Application must be explicitly approved before submission")
        return f"mock-receipt-{application.id}"
