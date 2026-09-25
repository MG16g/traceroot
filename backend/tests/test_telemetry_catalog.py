from unittest.mock import patch

from app.tools.telemetry_catalog import (
    get_telemetry_catalog,
    format_telemetry_catalog,
)


def test_get_telemetry_catalog():
    fake_logs = [
        {
            "service": "payment-service",
            "level": "ERROR",
            "message": "Database connection failed",
        },
        {
            "service": "payment-service",
            "level": "INFO",
            "message": "Payment request received",
        },
    ]

    fake_metrics = [
        {
            "service": "payment-service",
            "metric": "error_rate",
            "value": 0.42,
        },
        {
            "service": "payment-service",
            "metric": "latency_ms",
            "value": 820,
        },
    ]

    fake_deployments = [
        {
            "service": "payment-service",
            "status": "success",
            "version": "2.4.0",
        }
    ]

    def fake_load_telemetry(
        source: str,
        incident_id: str,
    ):
        assert incident_id == "INC-001"

        if source == "logs":
            return fake_logs

        if source == "metrics":
            return fake_metrics

        if source == "deployments":
            return fake_deployments

        return []

    with patch(
        "app.tools.telemetry_catalog.load_telemetry",
        side_effect=fake_load_telemetry,
    ):
        catalog = get_telemetry_catalog(
            "INC-001"
        )

    assert catalog["services"] == [
        "payment-service"
    ]

    assert catalog["log_levels"] == [
        "ERROR",
        "INFO",
    ]

    assert catalog["metrics"] == [
        "error_rate",
        "latency_ms",
    ]

    assert catalog["deployment_statuses"] == [
        "success"
    ]


def test_format_telemetry_catalog():
    catalog = {
        "services": [
            "payment-service",
        ],
        "log_levels": [
            "ERROR",
        ],
        "metrics": [
            "error_rate",
        ],
        "deployment_statuses": [
            "success",
        ],
    }

    result = format_telemetry_catalog(
        catalog
    )

    assert "payment-service" in result
    assert "ERROR" in result
    assert "error_rate" in result
    assert "success" in result