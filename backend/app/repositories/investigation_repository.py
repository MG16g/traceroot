from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.investigation import (
    InvestigationModel,
)


class InvestigationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        investigation: InvestigationModel,
    ) -> InvestigationModel:

        self.db.add(investigation)
        self.db.commit()
        self.db.refresh(investigation)

        return investigation

    def get_by_id(
        self,
        investigation_id: str,
    ) -> InvestigationModel | None:

        statement = select(
            InvestigationModel
        ).where(
            InvestigationModel.id
            == investigation_id
        )

        return self.db.scalar(statement)

    def get_latest_by_incident_id(
        self,
        incident_id: str,
    ) -> InvestigationModel | None:

        statement = (
            select(InvestigationModel)
            .where(
                InvestigationModel.incident_id
                == incident_id
            )
            .order_by(
                InvestigationModel.created_at.desc()
            )
            .limit(1)
        )

        return self.db.scalar(statement)