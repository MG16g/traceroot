from datetime import datetime
from typing import Any

from app.tools.telemetry_loader import load_telemetry


def get_deployments(
    incident_id: str,
    service: str | None = None,
    status: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
) -> list[dict[str, Any]]:

    deployments = load_telemetry(
        source="deployments",
        incident_id=incident_id,
    )

    results = []

    start_time = (
        datetime.fromisoformat(start_time)
        if start_time is not None
        else None
    )

    end_time = (
        datetime.fromisoformat(end_time)
        if end_time is not None
        else None
    )

    # filtering goes here
    for record in deployments:

        if service is not None:

            if record["service"].lower() != service.lower():
                 continue
        
                # metric filter
        if status is not None:
            if record["status"].lower() != status.lower():
                continue
        
        record_time = datetime.fromisoformat(record["timestamp"])
        
        if start_time is not None:
                # if record is BEFORE start → continue
            if record_time < start_time:
                    continue
        
        if end_time is not None:
                # if record is AFTER end → 
            if record_time > end_time:
                    continue
        
        results.append(record)


    return results