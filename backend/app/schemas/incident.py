from datetime import datetime
from enum import Enum

from pydantic import BaseModel,Field

from pydantic import BaseModel, Field, field_validator


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
        min_length=7,
        max_length=50,
        pattern=r"^INC-[0-9]+$",
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

    @field_validator(
        "title",
        "description",
        "service",
        mode="before",
    )
    @classmethod
    def strip_and_validate_text(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Value must be a string.")

        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "Field cannot contain only whitespace."
            )

        return cleaned

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
