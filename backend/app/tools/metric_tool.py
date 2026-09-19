from typing import Any
from datetime import datetime

from app.tools.telemetry_loader import load_telemetry


def query_metrics(
    incident_id: str,
    service: str | None = None,
    metric: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
) -> list[dict[str, Any]]:

    metrics = load_telemetry(
        source="metrics",
        incident_id=incident_id,
    )

    results = []

    start_dt = (
        datetime.fromisoformat(start_time)
        if start_time is not None
        else None
    )

    end_dt = (
        datetime.fromisoformat(end_time)
        if end_time is not None
        else None
    )

    for record in metrics:

        # service filter
        if service is not None:
            if record["service"].lower() != service.lower():
                continue

        # metric filter
        if metric is not None:
            if record["metric"].lower() != metric.lower():
                continue

        record_time = datetime.fromisoformat(record["timestamp"])

        if start_dt is not None:
        # if record is BEFORE start → continue
            if record_time < start_dt:
                continue

        if end_dt is not None:
        # if record is AFTER end → 
            if record_time > end_dt:
                continue

        results.append(record)

    return results