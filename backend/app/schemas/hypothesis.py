from enum import Enum

from pydantic import BaseModel,Field

class HypothesisStatus(str, Enum):
    PENDING = "pending"
    INVESTIGATING = "investigating"
    SUPPORTED = "supported"
    REJECTED = "rejected"

class Hypothesis(BaseModel):
    id : str
    incident_id : str
    description : str

    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    status: HypothesisStatus = HypothesisStatus.PENDING