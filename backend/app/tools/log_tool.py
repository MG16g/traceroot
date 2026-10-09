from typing import Any

from app.tools.telemetry_loader import load_telemetry


def search_logs(
    incident_id: str,
    service: str | None = None,
    level: str | None = None,
    query: str | None = None,
) -> list[dict[str, Any]]:

    logs = load_telemetry(
        source="logs",
        incident_id=incident_id,
    )

    results = []

    for log in logs:
        if service is not None:
            if log["service"].lower() != service.lower():
                continue

        if level is not None:
            if log["level"].lower() != level.lower():
                continue

        if query is not None:
            normalized_query = query.strip().lower()

            if normalized_query not in {"", "*"}:
                if normalized_query not in log["message"].lower():
                    continue

        results.append(log)

    return results