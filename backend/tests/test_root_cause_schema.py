import pytest
from pydantic import ValidationError

from app.schemas.root_cause import (
    RootCauseCandidate,
    RootCauseStatus,
)


def test_root_cause_candidate_schema():
    candidate = RootCauseCandidate(
        hypothesis_id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database connection pool exhaustion "
            "caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #1",
            "Evidence #2",
            "Evidence #3",
        ],
        contradicting_evidence=[],
        source_types=[
            "log",
            "metric",
        ],
        confidence=0.90,
        status=RootCauseStatus.SUPPORTED,
    )

    assert candidate.hypothesis_id == "HYP-001"
    assert candidate.incident_id == "INC-001"

    assert candidate.confidence == 0.90

    assert (
        candidate.status
        == RootCauseStatus.SUPPORTED
    )

    assert len(candidate.supporting_evidence) == 3
    assert len(candidate.source_types) == 2


def test_root_cause_confidence_cannot_exceed_one():
    with pytest.raises(ValidationError):
        RootCauseCandidate(
            hypothesis_id="HYP-001",
            incident_id="INC-001",
            description="Invalid confidence candidate",
            confidence=1.5,
        )


def test_root_cause_confidence_cannot_be_negative():
    with pytest.raises(ValidationError):
        RootCauseCandidate(
            hypothesis_id="HYP-001",
            incident_id="INC-001",
            description="Invalid confidence candidate",
            confidence=-0.2,
        )