from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class EvidenceSourceType(str, Enum):
    LOG = "log"
    METRIC = "metric"
    DEPLOYMENT = "deployment"
    RUNBOOK = "runbook"
    PAST_INCIDENT = "past_incident"


class Evidence(BaseModel):
    id: str
    incident_id: str
    source_type: EvidenceSourceType
    service: str
    content: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    relevance_score: float = Field(
        ge=0.0,
        le=1.0
    )