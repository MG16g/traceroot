from unittest.mock import MagicMock

from app.models.investigation import (
    InvestigationModel,
)

from app.repositories.investigation_repository import (
    InvestigationRepository,
)


def test_create_investigation():

    db = MagicMock()

    repository = InvestigationRepository(db)

    investigation = InvestigationModel(
        id="INV-001",
        incident_id="INC-001",
        status="completed",
        iteration=2,
        current_step="completed",
        executed_actions="[]",
    )

    result = repository.create(
        investigation
    )

    assert result is investigation

    db.add.assert_called_once_with(
        investigation
    )

    db.commit.assert_called_once()

    db.refresh.assert_called_once_with(
        investigation
    )


def test_get_investigation_by_id():

    db = MagicMock()

    investigation = InvestigationModel(
        id="INV-001",
        incident_id="INC-001",
        status="completed",
        iteration=2,
        current_step="completed",
        executed_actions="[]",
    )

    db.scalar.return_value = investigation

    repository = InvestigationRepository(db)

    result = repository.get_by_id(
        "INV-001"
    )

    assert result is investigation

    db.scalar.assert_called_once()


def test_get_latest_investigation_by_incident():

    db = MagicMock()

    investigation = InvestigationModel(
        id="INV-002",
        incident_id="INC-001",
        status="completed",
        iteration=2,
        current_step="completed",
        executed_actions="[]",
    )

    db.scalar.return_value = investigation

    repository = InvestigationRepository(db)

    result = repository.get_latest_by_incident_id(
        "INC-001"
    )

    assert result is investigation

    db.scalar.assert_called_once()


def test_get_investigation_history_by_incident():

    db = MagicMock()

    investigation_1 = InvestigationModel(
        id="INV-003",
        incident_id="INC-001",
        status="completed",
        iteration=3,
        current_step="completed",
        executed_actions="[]",
    )

    investigation_2 = InvestigationModel(
        id="INV-002",
        incident_id="INC-001",
        status="completed",
        iteration=2,
        current_step="completed",
        executed_actions="[]",
    )

    db.scalars.return_value.all.return_value = [
        investigation_1,
        investigation_2,
    ]

    repository = InvestigationRepository(db)

    result = repository.get_history_by_incident_id(
        "INC-001"
    )

    assert result == [
        investigation_1,
        investigation_2,
    ]

    db.scalars.assert_called_once()