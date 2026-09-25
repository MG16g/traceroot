from typing import Any

from app.tools.telemetry_loader import load_telemetry


def _safe_load(
    source: str,
    incident_id: str,
) -> list[dict[str, Any]]:
    """
    Load telemetry for the catalog.

    A missing telemetry source should not prevent the
    investigation from using other available sources.
    """
    try:
        return load_telemetry(
            source=source,
            incident_id=incident_id,
        )
    except Exception:
        return []


def _unique_values(
    records: list[dict[str, Any]],
    field: str,
) -> list[str]:
    """
    Extract unique non-empty values from a telemetry field.
    """
    values = {
        str(record[field])
        for record in records
        if record.get(field) is not None
    }

    return sorted(values)


def get_telemetry_catalog(
    incident_id: str,
) -> dict[str, Any]:
    """
    Discover telemetry values available for an incident.

    This catalog can be provided to the investigation
    planner so the LLM does not need to guess valid
    services, metrics, log levels, or deployment statuses.
    """

    logs = _safe_load(
        source="logs",
        incident_id=incident_id,
    )

    metrics = _safe_load(
        source="metrics",
        incident_id=incident_id,
    )

    deployments = _safe_load(
        source="deployments",
        incident_id=incident_id,
    )

    all_records = (
        logs
        + metrics
        + deployments
    )

    return {
        "services": _unique_values(
            all_records,
            "service",
        ),
        "log_levels": _unique_values(
            logs,
            "level",
        ),
        "metrics": _unique_values(
            metrics,
            "metric",
        ),
        "deployment_statuses": _unique_values(
            deployments,
            "status",
        ),
    }


def format_telemetry_catalog(
    catalog: dict[str, Any],
) -> str:
    """
    Convert the telemetry catalog into planner-friendly text.
    """

    services = catalog.get(
        "services",
        [],
    )

    log_levels = catalog.get(
        "log_levels",
        [],
    )

    metrics = catalog.get(
        "metrics",
        [],
    )

    deployment_statuses = catalog.get(
        "deployment_statuses",
        [],
    )

    return f"""
Available services:
{services}

Available log levels:
{log_levels}

Available metrics:
{metrics}

Available deployment statuses:
{deployment_statuses}
""".strip()