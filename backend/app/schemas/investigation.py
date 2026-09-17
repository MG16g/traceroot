from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis
from app.schemas.incident import Incident

class InvestigationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class InvestigationState(BaseModel):
    incident: Incident

    evidence: list[Evidence] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)

    current_step: str = "triage"
    iteration: int = Field(default=0, ge=0)

    status: InvestigationStatus = InvestigationStatus.PENDING

    final_report: str | None = None