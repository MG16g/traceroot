from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "traceroot-api",
    }


def test_readiness_database_connected():
    mock_connection = MagicMock()
    mock_connection.execute.return_value = MagicMock()

    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_connection

    with patch(
        "app.main.engine.connect",
        return_value=mock_context,
    ):
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "traceroot-api",
        "database": "connected",
    }

    mock_connection.execute.assert_called_once()


def test_readiness_database_unavailable():
    database_error = OperationalError(
        "SELECT 1",
        {},
        Exception("Connection refused"),
    )

    with patch(
        "app.main.engine.connect",
        side_effect=database_error,
    ):
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "service": "traceroot-api",
        "database": "unavailable",
    }


def test_health_remains_available_when_database_fails():
    database_error = OperationalError(
        "SELECT 1",
        {},
        Exception("Connection refused"),
    )

    with patch(
        "app.main.engine.connect",
        side_effect=database_error,
    ):
        response = client.get("/health")

    assert response.status_code == 200