from pydantic import BaseModel, Field
from datetime import datetime

class InvestigationRequest(BaseModel):
    incident_id: str = Field(
        min_length=1,
        description="Incident to investigate",
    )


class EvidenceResponse(BaseModel):
    id: str
    source_type: str
    service: str
    content: str
    relevance_score: float


class HypothesisResponse(BaseModel):
    id: str
    description: str
    supporting_evidence: list[str] = Field(
        default_factory=list
    )
    contradicting_evidence: list[str] = Field(
        default_factory=list
    )
    confidence: float
    status: str


class RootCauseResponse(BaseModel):
    description: str
    supporting_evidence: list[str] = Field(
        default_factory=list
    )
    contradicting_evidence: list[str] = Field(
        default_factory=list
    )
    source_types: list[str] = Field(
        default_factory=list
    )
    confidence: float
    status: str


class InvestigationResponse(BaseModel):
    incident_id: str

    status: str

    iteration: int

    current_step: str

    executed_actions: list[str] = Field(
        default_factory=list
    )

    evidence: list[EvidenceResponse] = Field(
        default_factory=list
    )

    hypotheses: list[HypothesisResponse] = Field(
        default_factory=list
    )

    root_cause: RootCauseResponse | None = None

    final_report: str | None = None

    error: str | None = None


class InvestigationHistoryItem(BaseModel):
    investigation_id: str
    incident_id: str
    status: str
    iteration: int
    current_step: str
    created_at: datetime
    root_cause_confidence: float | None = None