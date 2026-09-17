import pytest
from pydantic import ValidationError

from app.schemas.hypothesis import Hypothesis, HypothesisStatus


def test_create_hypothesis():
    hypothesis = Hypothesis(
        id="H-001",
        incident_id="INC-001",
        description="Payment service deployment introduced a database connection leak",
        supporting_evidence=["E-001", "E-002"],
        confidence=0.82,
    )

    assert hypothesis.id == "H-001"
    assert hypothesis.incident_id == "INC-001"
    assert hypothesis.confidence == 0.82
    assert hypothesis.status == HypothesisStatus.PENDING
    assert len(hypothesis.supporting_evidence) == 2


def test_hypothesis_defaults():
    hypothesis = Hypothesis(
        id="H-002",
        incident_id="INC-001",
        description="External payment provider is unavailable",
    )

    assert hypothesis.supporting_evidence == []
    assert hypothesis.contradicting_evidence == []
    assert hypothesis.confidence == 0.0
    assert hypothesis.status == HypothesisStatus.PENDING


def test_reject_invalid_confidence():
    with pytest.raises(ValidationError):
        Hypothesis(
            id="H-003",
            incident_id="INC-001",
            description="Database server is unavailable",
            confidence=1.5,
        )