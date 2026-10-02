from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

import json

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.core.dependencies import get_db

from app.repositories.incident_repository import (
    IncidentRepository,
)

from app.schemas.api import (
    InvestigationComparisonResponse,
    InvestigationHistoryItem,
    InvestigationRequest,
    InvestigationResponse,
)

from app.schemas.incident import Incident

from app.services.investigation_service import (
    build_investigation_response,
    compare_investigations,
    get_investigation_history,
    get_investigation_by_id,
    get_latest_investigation,
    persist_investigation,
    run_investigation,
    stream_investigation,
)


router = APIRouter(
    prefix="/api/investigations",
    tags=["Investigations"],
)


@router.post(
    "",
    response_model=InvestigationResponse,
)
def create_investigation(
    request: InvestigationRequest,
    db: Session = Depends(get_db),
) -> InvestigationResponse:

    repository = IncidentRepository(db)

    incident_model = repository.get_by_id(
        request.incident_id
    )

    if incident_model is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Incident {request.incident_id} "
                "not found"
            ),
        )

    # Convert SQLAlchemy model into the Pydantic/domain
    # model expected by the investigation engine.
    incident = Incident(
        id=incident_model.id,
        title=incident_model.title,
        description=incident_model.description,
        service=incident_model.service,
        severity=incident_model.severity,
        status=incident_model.status,
        created_at=incident_model.created_at,
    )

    response = run_investigation(
        incident
    )

    persist_investigation(
        db=db,
        response=response,
    )

    return response

@router.get(
        "/{incident_id}/history",
        response_model=list[InvestigationHistoryItem],
    )
def get_investigation_history_endpoint(
        incident_id: str,
        db: Session = Depends(get_db),
    ) -> list[InvestigationHistoryItem]:

        return get_investigation_history(
            db=db,
            incident_id=incident_id,
        )

@router.get(
    "/runs/{investigation_id}",
    response_model=InvestigationResponse,
)
def get_investigation_run(
    investigation_id: str,
    db: Session = Depends(get_db),
) -> InvestigationResponse:

    response = get_investigation_by_id(
        db=db,
        investigation_id=investigation_id,
    )

    if response is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Investigation "
                f"{investigation_id} not found"
            ),
        )

    return response


@router.get(
    "/compare/{baseline_investigation_id}/{comparison_investigation_id}",
)
def compare_investigation_runs(
    baseline_investigation_id: str,
    comparison_investigation_id: str,
    db: Session = Depends(get_db),
):
    """
    Compare two persisted investigation runs.

    Both investigation runs must exist and belong
    to the same incident.
    """

    try:
        comparison = compare_investigations(
            db=db,
            baseline_investigation_id=baseline_investigation_id,
            comparison_investigation_id=comparison_investigation_id,
        )
        

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if comparison is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "One or both investigation runs "
                "were not found"
            ),
        )

    return comparison


@router.get(
    "/{incident_id}",
    response_model=InvestigationResponse,
)
def get_investigation(
    incident_id: str,
    db: Session = Depends(get_db),
) -> InvestigationResponse:

    response = get_latest_investigation(
        db=db,
        incident_id=incident_id,
    )

    if response is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No investigation found for "
                f"incident {incident_id}"
            ),
        )

    return response


def build_progress_message(
    step: str,
) -> str:
    messages = {
        "action_selected":
            "Selected the next investigation action.",

        "evidence_collected":
            "Collected telemetry evidence.",

        "no_results":
            "Investigation action returned no results.",

        "hypothesis_updated":
            "Updated the incident hypothesis.",

        "root_cause_evaluated":
            "Evaluated the root-cause candidate.",

        "duplicate_action_skipped":
            "Skipped a duplicate investigation action.",

        "no_hypothesis_evidence":
            "No evidence available for hypothesis generation.",

        "no_root_cause_candidate":
            "No root-cause candidate established yet.",

        "tool_error":
            "An investigation tool encountered an error.",

        "completed":
            "Generated the final RCA report.",
    }

    return messages.get(
        step,
        f"Investigation step: {step}",
    )

@router.get("/stream/{incident_id}")
def stream_investigation_endpoint(
    incident_id: str,
    db: Session = Depends(get_db),
):
    repository = IncidentRepository(db)

    incident_model = repository.get_by_id(
        incident_id
    )

    if incident_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found",
        )

    incident = Incident(
        id=incident_model.id,
        title=incident_model.title,
        description=incident_model.description,
        service=incident_model.service,
        severity=incident_model.severity,
        status=incident_model.status,
        created_at=incident_model.created_at,
    )

    def event_generator():
        final_state = None

        try:
            started = {
                "event": "started",
                "incident_id": incident_id,
                "message": "Investigation started",
            }

            yield (
                f"event: started\n"
                f"data: {json.dumps(started)}\n\n"
            )

            for state in stream_investigation(
                incident
            ):
                final_state = state

                step = state.get(
                    "current_step",
                    "unknown",
                )

                iteration = state.get(
                    "iteration",
                    0,
                )

                progress = {
                    "event": "progress",
                    "incident_id": incident_id,
                    "step": step,
                    "iteration": iteration,
                    "message": build_progress_message(
                        step
                    ),
                }

                yield (
                    f"event: progress\n"
                    f"data: {json.dumps(progress)}\n\n"
                )

            if final_state is None:
                raise RuntimeError(
                    "Investigation completed without graph state"
                )

            response = build_investigation_response(
                result=final_state,
                incident_id=incident_id,
            )

            persist_investigation(
                db=db,
                response=response,
            )

            completed = {
                "event": "completed",
                "incident_id": incident_id,
                "message": "Investigation completed",
                "data": response.model_dump(),
            }

            yield (
                f"event: completed\n"
                f"data: {json.dumps(completed)}\n\n"
            )

        except Exception as exc:
            error = {
                "event": "investigation_error",
                "incident_id": incident_id,
                "message": str(exc),
            }

            yield (
                f"event: investigation_error\n"
                f"data: {json.dumps(error)}\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )