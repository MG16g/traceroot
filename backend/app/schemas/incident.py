from datetime import datetime
from enum import Enum

from pydantic import BaseModel,Field


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class IncidentCreate(BaseModel):
    id: str = Field(
        min_length=3,
        max_length=50,
    )
    title: str = Field(
        min_length=3,
        max_length=200,
    )
    description: str = Field(
        min_length=3,
    )
    service: str = Field(
        min_length=2,
        max_length=100,
    )
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN

class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus

class Incident(BaseModel):
    id:str
    title: str = Field(min_length=3,max_length=200)
    description: str
    service: str
    severity: IncidentSeverity
    status: IncidentStatus=IncidentStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.utcnow)
