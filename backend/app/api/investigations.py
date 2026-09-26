from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.dependencies import get_db

from app.repositories.incident_repository import (
    IncidentRepository,
)

from app.schemas.api import (
    InvestigationRequest,
    InvestigationResponse,
)

from app.schemas.incident import Incident

from app.services.investigation_service import (
    get_latest_investigation,
    persist_investigation,
    run_investigation,
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