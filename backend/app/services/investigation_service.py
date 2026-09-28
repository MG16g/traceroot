import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.investigation import InvestigationModel
from app.repositories.investigation_repository import InvestigationRepository

from app.orchestration.investigation_graph import (
    build_investigation_graph,
)

from app.schemas.investigation import InvestigationState

from app.schemas.api import (
    InvestigationResponse,
    EvidenceResponse,
    HypothesisResponse,
    RootCauseResponse,
)


def run_investigation(incident) -> InvestigationResponse:
    """
    Run the TraceRoot investigation graph for an incident
    and convert the internal graph state into the public
    API response contract.
    """

    graph = build_investigation_graph()

    initial_state = InvestigationState(
        incident=incident,
    )

    result = graph.invoke(initial_state)

    return build_investigation_response(
        result=result,
        incident_id=incident.id,
    )

def stream_investigation(incident):
    """
    Stream graph state snapshots as TraceRoot investigates
    an incident.

    The caller can use intermediate snapshots for progress
    updates and the final snapshot to build/persist the
    InvestigationResponse without executing the graph twice.
    """

    graph = build_investigation_graph()

    initial_state = InvestigationState(
        incident=incident,
    )

    yield from graph.stream(
        initial_state,
        stream_mode="values",
    )

def build_investigation_response(
    result: dict,
    incident_id: str,
) -> InvestigationResponse:

    evidence_items = [
        EvidenceResponse(
            id=evidence.id,
            source_type=evidence.source_type.value,
            service=evidence.service,
            content=evidence.content,
            relevance_score=evidence.relevance_score,
        )
        for evidence in result.get("evidence", [])
    ]

    hypothesis_items = [
        HypothesisResponse(
            id=hypothesis.id,
            description=hypothesis.description,
            supporting_evidence=(
                hypothesis.supporting_evidence
            ),
            contradicting_evidence=(
                hypothesis.contradicting_evidence
            ),
            confidence=hypothesis.confidence,
            status=hypothesis.status.value,
        )
        for hypothesis in result.get(
            "hypotheses",
            [],
        )
    ]

    candidate = result.get(
        "root_cause_candidate"
    )

    root_cause = None

    if candidate is not None:
        root_cause = RootCauseResponse(
            description=candidate.description,
            supporting_evidence=(
                candidate.supporting_evidence
            ),
            contradicting_evidence=(
                candidate.contradicting_evidence
            ),
            source_types=[
                (
                    source_type.value
                    if hasattr(source_type, "value")
                    else str(source_type)
                )
                for source_type in candidate.source_types
            ],
            confidence=candidate.confidence,
            status=(
                candidate.status.value
                if hasattr(candidate.status, "value")
                else str(candidate.status)
            ),
        )

    status = result.get(
        "status",
        "completed",
    )

    if hasattr(status, "value"):
        status = status.value

    return InvestigationResponse(
        incident_id=incident_id,
        status=status,
        iteration=result.get(
            "iteration",
            0,
        ),
        current_step=result.get(
            "current_step",
            "unknown",
        ),
        executed_actions=result.get(
            "executed_actions",
            [],
        ),
        evidence=evidence_items,
        hypotheses=hypothesis_items,
        root_cause=root_cause,
        final_report=result.get(
            "final_report"
        ),
        error=result.get(
            "error"
        ),
    )

def persist_investigation(
    db: Session,
    response: InvestigationResponse,
) -> InvestigationModel:

    repository = InvestigationRepository(db)

    root_cause_json = None

    if response.root_cause is not None:
        root_cause_json = json.dumps(
            response.root_cause.model_dump()
        )

    evidence_json = json.dumps(
        [
            item.model_dump()
            for item in response.evidence
        ]
    )

    hypotheses_json = json.dumps(
        [
            item.model_dump()
            for item in response.hypotheses
        ]
    )

    investigation = InvestigationModel(
        id=f"INV-{uuid4().hex[:12].upper()}",
        incident_id=response.incident_id,
        status=response.status,
        iteration=response.iteration,
        current_step=response.current_step,
        executed_actions=json.dumps(
            response.executed_actions
        ),
        evidence=evidence_json,
        hypotheses=hypotheses_json,
        root_cause=root_cause_json,
        final_report=response.final_report,
        error=response.error,
    )

    return repository.create(
        investigation
    )

def investigation_model_to_response(
    model: InvestigationModel,
) -> InvestigationResponse:

    executed_actions = json.loads(
        model.executed_actions or "[]"
    )

    evidence = json.loads(
        model.evidence or "[]"
    )

    hypotheses = json.loads(
        model.hypotheses or "[]"
    )

    root_cause = None

    if model.root_cause:
        root_cause = json.loads(
            model.root_cause
        )

    return InvestigationResponse(
        incident_id=model.incident_id,
        status=model.status,
        iteration=model.iteration,
        current_step=model.current_step,
        executed_actions=executed_actions,
        evidence=evidence,
        hypotheses=hypotheses,
        root_cause=root_cause,
        final_report=model.final_report,
        error=model.error,
    )

def get_latest_investigation(
    db: Session,
    incident_id: str,
) -> InvestigationResponse | None:

    repository = InvestigationRepository(db)

    model = repository.get_latest_by_incident_id(
        incident_id
    )

    if model is None:
        return None

    return investigation_model_to_response(
        model
    )