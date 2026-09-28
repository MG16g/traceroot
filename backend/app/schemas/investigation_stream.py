from typing import Any

from pydantic import BaseModel


class InvestigationStreamEvent(BaseModel):
    event: str
    incident_id: str
    node: str | None = None
    step: str | None = None
    iteration: int | None = None
    message: str
    data: dict[str, Any] | None = None