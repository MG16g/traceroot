from app.core.database import SessionLocal
from app.models.evidence import EvidenceModel
from app.models.incident import IncidentModel


def test_incident_has_multiple_evidence_records():
    db = SessionLocal()

    try:
        # Cleanup from a previous failed test
        existing = db.get(IncidentModel, "INC-REL-001")

        if existing:
            db.delete(existing)
            db.commit()

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

        db.add(incident)
        db.commit()

        db.expire_all()

        retrieved = db.get(
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

    finally:
        incident = db.get(
            IncidentModel,
            "INC-REL-001",
        )

        if incident:
            db.delete(incident)
            db.commit()

        db.close()