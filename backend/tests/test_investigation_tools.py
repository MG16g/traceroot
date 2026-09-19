from app.tools.deployment_tool import get_deployments
from app.tools.log_tool import search_logs
from app.tools.metric_tool import query_metrics


def test_inc001_investigation_evidence_is_discoverable():

    deployments = get_deployments(
        "INC-001",
        service="payment-service",
        start_time="2026-09-18T14:00:00Z",
        end_time="2026-09-18T14:15:00Z",
    )

    logs = search_logs(
        "INC-001",
        service="payment-service",
        level="ERROR",
        query="connection",
    )

    metrics = query_metrics(
        "INC-001",
        service="payment-service",
        metric="db_connection_utilization",
        start_time="2026-09-18T14:05:00Z",
        end_time="2026-09-18T14:12:00Z",
    )

    assert len(deployments) == 1
    assert deployments[0]["version"] == "2.4.0"

    assert len(logs) > 0
    assert all(log["level"] == "ERROR" for log in logs)

    assert len(metrics) == 4
    assert metrics[-1]["value"] == 98.0