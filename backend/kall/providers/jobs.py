from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol


@dataclass
class DiscoveredJob:
    source: str
    external_id: str | None
    company: str
    title: str
    description: str
    url: str
    location: str | None = None
    posted_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class JobBoardProvider(Protocol):
    name: str
    async def collect(self, company_name: str, board_key: str) -> list[DiscoveredJob]: ...
