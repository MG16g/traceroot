
from sqlalchemy.orm import Session

from app.models.evidence import EvidenceModel
from app.models.incident import IncidentModel


def test_incident_has_multiple_evidence_records(
    db_session: Session,
) -> None:
    incident = IncidentModel(
        id="INC-REL-001",
        title="Payment service degradation",
        description="Payment requests are failing",
        service="payment-service",
        severity="critical",
        status="open",
    )

    evidence_1 = EvidenceModel(
        id="E-REL-001",
        incident_id="INC-REL-001",
        source_type="log",
        service="payment-service",
        content="DBConnectionPoolExhausted",
        relevance_score=0.95,
    )

    evidence_2 = EvidenceModel(
        id="E-REL-002",
        incident_id="INC-REL-001",
        source_type="metric",
        service="payment-service",
        content="Database connection utilization reached 98%",
        relevance_score=0.90,
    )

    incident.evidence.extend([
        evidence_1,
        evidence_2,
    ])

    db_session.add(incident)
    db_session.commit()

    db_session.expire_all()

    retrieved = db_session.get(
        IncidentModel,
        "INC-REL-001",
    )

    assert retrieved is not None
    assert len(retrieved.evidence) == 2

    evidence_ids = {
        evidence.id
        for evidence in retrieved.evidence
    }

    assert evidence_ids == {
        "E-REL-001",
        "E-REL-002",
    }
