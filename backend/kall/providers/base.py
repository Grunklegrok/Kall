from typing import Protocol

from kall.models.core import Application


class ATSConnector(Protocol):
    name: str

    def can_prepare(self, job_url: str) -> bool: ...

    def submit(self, application: Application) -> str:
        ...
