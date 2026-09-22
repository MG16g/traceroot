from enum import Enum

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis
from app.schemas.incident import Incident

class InvestigationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class InvestigationAction(str, Enum):
    SEARCH_LOGS = "search_logs"
    QUERY_METRICS = "query_mertics"
    GET_DEPLOYMENTS = "get_deployments"
    STOP = "stop"

class InvestigationDecision(BaseModel):
    action: InvestigationAction
    reason: str
    parameters: dict[str, Any] = Field(default_factory=dict)



class InvestigationState(BaseModel):
    incident: Incident

    evidence: list[Evidence] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)

    current_step: str = "triage"
    iteration: int = Field(default=0, ge=0)

    status: InvestigationStatus = InvestigationStatus.PENDING

    current_decision: InvestigationDecision | None = None

    error: str | None = None

    final_report: str | None = None