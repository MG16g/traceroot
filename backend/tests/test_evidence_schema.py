import pytest
from pydantic import ValidationError

from app.schemas.evidence import Evidence, EvidenceSourceType


def test_create_valid_evidence():
    evidence = Evidence(
        id="E-001",
        incident_id="INC-001",
        source_type=EvidenceSourceType.LOG,
        service="payment-service",
        content="DBConnectionPoolExhausted",
        relevance_score=0.95,
    )

    assert evidence.id == "E-001"
    assert evidence.incident_id == "INC-001"
    assert evidence.source_type == EvidenceSourceType.LOG
    assert evidence.relevance_score == 0.95


def test_reject_invalid_relevance_score():
    with pytest.raises(ValidationError):
        Evidence(
            id="E-002",
            incident_id="INC-001",
            source_type=EvidenceSourceType.METRIC,
            service="payment-service",
            content="Database connection utilization reached 98%",
            relevance_score=1.5,
        )